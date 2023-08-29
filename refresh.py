import os

import pandas as pd
import sql.get_table
import time
import datetime
import logging
import sys

import tools.clean_processes

logger = logging.getLogger()
logger.setLevel(logging.INFO)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

query_fut_upd = f"""
BEGIN;
MERGE INTO public.futquotesdiff fqd
USING public.futquotes fq
ON fq.code = fqd.code
WHEN MATCHED THEN
UPDATE SET bid = fq.bid, ask = fq.ask, volume = fq.volume, openinterest = fq.openinterest, bidamount=fq.bidamount, askamount=fq.askamount, 
bid_inc = fq.bid - fqd.bid, ask_inc = fq.ask-fqd.ask, volume_inc = fq.volume-fqd.volume, updated_at=fq.updated_at, last_upd=NOW(),
volume_wa = coalesce(volume_wa,0)* 119/120 + (fq.volume-fqd.volume)/120,   
min_5mins = case when  EXTRACT (MINUTE FROM fqd.updated_at) <> EXTRACT (MINUTE FROM fq.updated_at) and extract (minute from now())%%5=0 then fq.ask else least(fqd.min_5mins, fq.ask) end,
max_5mins = case when  EXTRACT (MINUTE FROM fqd.updated_at) <> EXTRACT (MINUTE FROM fq.updated_at) and extract (minute from now())%%5=0 then fq.bid else GREATEST(fqd.max_5mins, fq.bid) end
WHEN NOT MATCHED THEN
INSERT (code, bid, bidamount, ask, askamount, volume, openinterest, bid_inc, ask_inc, volume_inc, updated_at, last_upd, volume_wa, min_5mins, max_5mins) 
VALUES (fq.code, fq.bid, fq.bidamount, fq.ask, fq.askamount, fq.volume, fq.openinterest, 0, 0, 0, fq.updated_at, NOW(), 0, fq.ask, fq.bid); 
COMMIT;
"""


query_sec_upd=f"""
BEGIN;
MERGE INTO public.secquotesdiff fqd
USING public.secquotes fq
ON fq.code = fqd.code
WHEN MATCHED THEN
UPDATE SET 
bid = fq.bid, 
ask = fq.ask, 
volume = fq.volume, 
bidamount=fq.bidamount, 
askamount=fq.askamount, 
bid_inc = fq.bid - fqd.bid, 
ask_inc = fq.ask-fqd.ask, 
volume_inc = fq.volume-fqd.volume, 
updated_at=fq.updated_at, 
last_upd=NOW(),
volume_wa = coalesce(volume_wa,0)*119/120 + (fq.volume-fqd.volume)/120,
min_5mins = case when  EXTRACT (MINUTE FROM fqd.updated_at) <> EXTRACT (MINUTE FROM fq.updated_at) and extract (minute from now())%%5=0 then fq.ask else least(fqd.min_5mins, fq.ask) end,
max_5mins = case when  EXTRACT (MINUTE FROM fqd.updated_at) <> EXTRACT (MINUTE FROM fq.updated_at) and extract (minute from now())%%5=0 then fq.bid else GREATEST(fqd.max_5mins, fq.bid) end
WHEN NOT MATCHED THEN
INSERT (code, bid, bidamount, ask, askamount, volume, bid_inc, ask_inc, volume_inc, updated_at, last_upd, volume_wa, min_5mins, max_5mins) 
VALUES (fq.code, fq.bid, fq.bidamount, fq.ask, fq.askamount, fq.volume, 0, 0, 0, fq.updated_at, NOW(), 0, fq.ask, fq.bid);
COMMIT;
"""


query_sig_upd = """
insert into public.signal_arch(tstz, code, date_discovery, channel_source, news_time, min_val, max_val, mean_val, volume, board, min, max, last_volume, count)
select * from public.signal;
"""

query_orders_by_events = """
        begin;
        with shape_update as (
        update orders_event_activator oea
        set is_activated = true,
        activate_time = now()
        from event_news en
        where is_activated = false 
        and oea.ticker = en.code 
        and oea.keyword = en.keyword
        and news_time between start_date and end_date
        and (length(oea.channel_source) = 0 or oea.channel_source = en.channel_source)
        returning id
        )
        update orders_my om
        set state = 1 where state=0 and om.activate_news in (select id from shape_update);
        commit;
        begin;
        with shape_update as (
        update orders_event_activator_jumps oeaj
        set is_activated = true,
        activate_time = now()
        from events_jumps_hist ejh
        where is_activated = false 
        and oeaj.ticker = ejh.code 
        and ejh.process_time between oeaj.start_date and oeaj.end_date
		and abs(ejh.jump_prct) > coalesce(oeaj.jump_prct,0)
		and abs(ejh.out_prct) > coalesce(oeaj.out_prct,0)
		and ejh.volume_peak > coalesce(oeaj.volume_peak,0)
		and abs(ejh.out_std) > coalesce(oeaj.out_std,0)
        returning id
        )
        update orders_my om
        set state = 1 where state=0 and om.activate_jump in (select id from shape_update);
        commit;
"""


def update():
    # update secquotesdiff and futquotesdiff
    sql.get_table.exec_query(query_fut_upd)
    sql.get_table.exec_query(query_sec_upd)

    # store events
    try:
        store_jump_events()
    except Exception as e:
        logger.error(f"store jump events{e}")
    query_fut = "select max(updated_at), count(*) as cnt from public.futquotesdiff;"
    query_sec = "select max(updated_at), count(*) as cnt from public.secquotesdiff;"

    last_sec = sql.get_table.query_to_list(query_sec)[0]
    last_fut = sql.get_table.query_to_list(query_fut)[0]
    logger.info(f"\nsec: {last_sec}\nfut: {last_fut}")

    # activate orders by events
    sql.get_table.exec_query(query_orders_by_events)

    # deactivate old signals
    query_deact = "update public.orders_my set state=0	where now() > end_time"
    sql.get_table.exec_query(query_deact)


    # process stop loss take profit
    query_sltp = """
    select case 
    when (direction = 1 and bid > take_profit) or (direction = -1 and ask < take_profit) then 1
    else -1 end as tpsl, 
    * from allquotes
    where end_time is null and
    (
    (direction = 1 and bid > take_profit) or (direction = -1 and ask < take_profit)
    or
    (direction = -1 and bid > stop_loss) or (direction = 1 and ask < stop_loss)
    )
    """
    for sltp_line in sql.get_table.query_to_list(query_sltp):
        deact_query = f"update public.orders_my set state = 0, end_time=now() where id = {sltp_line['id']}"
        sql.get_table.exec_query(deact_query)
        if sltp_line['tpsl'] == 1: #take_profit
            new_order = f"""insert into public.orders_my(state, quantity, comment, remains, parent_id, barrier, max_amount, pause, code, direction, start_time)
            values(1,{-sltp_line['remains']},'take profit',0, {sltp_line['id']},{sltp_line['take_profit']}, 1,1,'{sltp_line['code']}',{-sltp_line['direction']} ,now()) 
            """
            sql.get_table.exec_query(new_order)
        else: #stop_loss
            new_order = f"""insert into public.orders_my(state, quantity, comment, remains, parent_id, barrier, max_amount, pause, code, direction, start_time)
            values(1,{-sltp_line['remains']},'stop loss',0, {sltp_line['id']},{sltp_line['stop_loss']}, 1,1,'{sltp_line['code']}',{-sltp_line['direction']} ,now()) 
            """
            sql.get_table.exec_query(new_order)
    return


def compose_td_datetime(curr_time):
    now = datetime.datetime.now()
    my_datetime = datetime.datetime.strptime(curr_time, "%H:%M:%S").time()
    return now.replace(hour=my_datetime.hour, minute=my_datetime.minute, second=my_datetime.second, microsecond=0)


def get_pos(sec_code):
    query = f"""SELECT * FROM public.united_pos where code='{sec_code}' LIMIT 1"""
    q_res = sql.get_table.exec_query(query).mappings().all()
    return 0 if len(q_res) == 0 else q_res[0]['pos']


def process_signal():
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

        if signal['max'] > signal['max_val'] * 2 - signal['min_val']: #buy
            direction = 1
            barrier = signal['mean_val'] * 1.003
        elif signal['min'] < signal['min_val'] * 2 - signal['max_val']: #sell
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

        if state == 1: # если все всерьез
            if direction * cur_pos > 0: # и надо еще купить
                if abs(cur_pos) > abs(3*qty):
                    state = 0
            else: # в разные стороны - закрываем
                qty = min(max(abs(qty), abs(cur_pos)), 3*qty) # между 1 и 3 лямами

        # и обнуляем текущие ордера hft
        if state == 1: # если после фильтрации все еще все всерьез
            query = f"""
            begin;
            update public.orders_my  
            set state = 0,
            end_time = coalesce(end_time, now())
            where left (comment,3) = 'HFT'
            and state = 1
            and code = '{code}';
            commit;
            """
            sql.get_table.exec_query(query)

        query = f"""
            BEGIN;
            insert into public.orders_my (state, quantity, comment, remains, barrier, max_amount, pause, code, end_time, start_time)
            values({state},{qty*direction},'{comment}',0,{barrier}, {qty/2},1,'{code}','{end_time}', now());
            COMMIT;
            """
        logger.debug(query)
        sql.get_table.exec_query(query)
    logger.info("process signal out")


def store_jump_events():
    query = "select * from public.jump_events;"
    df_jumps = pd.DataFrame(sql.get_table.exec_query(query))
    if len(df_jumps)>0:
        sql.get_table.df_to_sql(df_jumps, 'events_jumps_hist')


start_refresh = compose_td_datetime("09:00:00")
end_refresh = compose_td_datetime("23:30:00")


if __name__ == '__main__':
    logger.info("starting refresh")
    if not tools.clean_processes.clean_proc("refresh", os.getpid(), 999999):
        print("something is already running")
        exit(0)

    while start_refresh <= datetime.datetime.now() < end_refresh:
        logger.info(datetime.datetime.now())
        try:
            update()
            sql.get_table.exec_query(query_sig_upd)
        except Exception as e:
            logger.error(f"{e}")

        # process_signal()
        time.sleep(0.5 - (time.time() % 0.5))
