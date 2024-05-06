import logging
from datetime import datetime

import sql.get_table
from refresh.queries import get_query_sl_tp
from tools.utils import sync_timed
from transactions import get_pos

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


@sync_timed()
def update_orders_state():
    # process stop loss take profit, ставим стейт = 0 и вводим противоположную заявку
    for sltp_line in sql.get_table.query_to_list(get_query_sl_tp()):
        deact_query = f"update public.orders_my set state = 0, end_time=now() where id = {sltp_line['id']}"
        sql.get_table.exec_query(deact_query)
        if sltp_line['tpsl'] == 1:  # take_profit
            new_order = f"""insert into public.orders_my(state, quantity, comment, remains, parent_id, barrier, max_amount, pause, code, direction, start_time)
            values(1,{-sltp_line['remains']},'take profit',0, {sltp_line['id']},{sltp_line['take_profit']}, 1,1,'{sltp_line['code']}',{-sltp_line['direction']} ,now()) 
            """
            sql.get_table.exec_query(new_order)
        else:  # stop_loss
            new_order = f"""insert into public.orders_my(state, quantity, comment, remains, parent_id, barrier, max_amount, pause, code, direction, start_time)
            values(1,{-sltp_line['remains']},'stop loss',0, {sltp_line['id']},{sltp_line['stop_loss']}, 1,1,'{sltp_line['code']}',{-sltp_line['direction']} ,now()) 
            """
            sql.get_table.exec_query(new_order)


def process_signal():
    """
    попытка мгновенно вставать в позицию по новостям из profitgate
    :return:
    """
    logger.info("process signal in")
    query = """
    SELECT * FROM public.signal_arch where 1=1 
    and ('HFT' || channel_source ||news_time || ':00') not in (select comment from orders_my)
    and tstz > now() - interval '1 minute'
    order by tstz desc limit 10;
    """
    quotes = sql.get_table.exec_query(query)
    signals = (quotes.mappings().all())

    for signal in signals:
        logger.info(f"processing signal {signal}")
        comment = 'HFT' + signal['channel_source'] + str(signal['news_time'])
        code = signal['code']
        end_time = signal['news_time'] + datetime.timedelta(minutes=3)

        if signal['max'] > signal['max_val'] * 2 - signal['min_val']:  # buy
            direction = 1
            barrier = signal['mean_val'] * 1.003
        elif signal['min'] < signal['min_val'] * 2 - signal['max_val']:  # sell
            direction = -1
            barrier = signal['mean_val'] / 1.003
        else:
            logger.debug("clauses are not fulfilled")
            continue

        state = 1 if signal['channel_source'] == 'ProfitGateClub' else 0

        query = f"select round(1100000/(bid * lot)) as qty from public.allquotes_collat where code = '{code}'"
        quotes = sql.get_table.exec_query(query)

        qty = (quotes.mappings().all())[0]['qty']
        cur_pos = get_pos(code)
        # если открыто много - ничего не делаем, если открыто не в ту сторону-  закрырваем 3х

        if state == 1:  # если все всерьез
            if direction * cur_pos > 0:  # и надо еще купить
                if abs(cur_pos) > abs(3 * qty):
                    state = 0
            else:  # в разные стороны - закрываем
                qty = min(max(abs(qty), abs(cur_pos)), 3 * qty)  # между 1 и 3 лямами

        # и обнуляем текущие ордера hft
        if state == 1:  # если после фильтрации все еще все всерьез
            query = f"""
            update public.orders_my  
            set state = 0,
            end_time = coalesce(end_time, now())
            where left (comment,3) = 'HFT'
            and state = 1
            and code = '{code}';
            """
            sql.get_table.exec_query(query)

        query = f"""
            insert into public.orders_my (state, quantity, comment, remains, barrier, max_amount, pause, code, end_time, start_time)
            values({state},{qty * direction},'{comment}',0,{barrier}, {qty / 2},1,'{code}','{end_time}', now());
            """
        logger.debug(query)
        sql.get_table.exec_query(query)
    logger.info("process signal out")


update_orders_state()
