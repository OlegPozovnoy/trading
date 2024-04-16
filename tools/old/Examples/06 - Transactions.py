import datetime
import random
import signal
from time import sleep
import sql.get_table
from QuikPy.QuikPy import QuikPy  # Работа с QUIK из Python через LUA скрипты QuikSharp
import pandas as pd
from _decimal import Decimal
import logging
import os
import uuid
from dotenv import load_dotenv, find_dotenv

from tinkoff.invest import (
    Client,
    OrderDirection,
    OrderType,
    PostOrderResponse,
)

#load_dotenv(dotenv_path='./../my.env')
load_dotenv(find_dotenv('my.env', True))


TOKEN = os.environ["TOKEN_WRITE"]

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

client = type((Client(TOKEN))).__enter__((Client(TOKEN)))
account_id = os.environ["tcs_account_id"]

reply = False
global_reply = None
engine = sql.get_table.engine


class OrderProcesser:
    def __init__(self):
        self.tasks_list = []

    def add_task(self, task, timeout):
        if task[0] not in [item[0][0] for item in self.tasks_list]:  # item[0] order item[0][0] - key
            self.tasks_list.append((task, datetime.datetime.now() + datetime.timedelta(seconds=timeout)))
            self.tasks_list = sorted(self.tasks_list, key=lambda x: x[1])
            return True  # task is scheduled
        return False  # task exist

    def do_tasks(self):
        tasks_to_do = [task for task in self.tasks_list if task[1] < datetime.datetime.now()]
        self.tasks_list = self.tasks_list[len(tasks_to_do):]
        print(f"Order oricessor tasks to do {tasks_to_do}")
        print(f"Order oricessor tasks_list {self.tasks_list}")
        return tasks_to_do


def OnTransReply(data):
    global reply
    global global_reply
    """Обработчик события ответа на транзакцию пользователя"""
    global_reply = data['data']
    reply = True


def OnOrder(data):
    """Обработчик события получения новой / изменения существующей заявки"""
    print('OnOrder')
    print(data['data'])  # Печатаем полученные данные


def OnTrade(data):
    """Обработчик события получения новой / изменения существующей сделки
    Не вызывается при закрытии сделки
    """
    print('OnTrade')
    print(data['data'])  # Печатаем полученные данные


def OnFuturesClientHolding(data):
    """Обработчик события изменения позиции по срочному рынку"""
    print('OnFuturesClientHolding')
    print(data['data'])  # Печатаем полученные данные


def OnDepoLimit(data):
    """Обработчик события изменения позиции по инструментам"""
    print('OnDepoLimit')
    print(data['data'])  # Печатаем полученные данные


def OnDepoLimitDelete(data):
    """Обработчик события удаления позиции по инструментам"""
    print('OnDepoLimitDelete')
    print(data['data'])  # Печатаем полученные данные


def get_quotes(classCode, secCode):
    if classCode == 'SPBFUT':
        query = f"""SELECT * FROM public.futquotes where code='{secCode}' LIMIT 1"""
    else:
        query = f"""SELECT * FROM public.secquotes where code='{secCode}' LIMIT 1"""
    quotes = sql.get_table.exec_query(query)
    return quotes.mappings().all()


def get_diff(classCode, secCode):
    if classCode == 'SPBFUT':
        query = f"""SELECT * FROM public.futquotesdiff where code='{secCode}' LIMIT 1"""
    else:
        query = f"""SELECT * FROM public.secquotesdiff where code='{secCode}' LIMIT 1"""
    quotes = sql.get_table.exec_query(query)
    return quotes.mappings().all()


def get_pos(secCode):
    query = f"""SELECT * FROM public.united_pos where code='{secCode}' LIMIT 1"""
    q_res = sql.get_table.exec_query(query).mappings().all()
    return 0 if len(q_res) == 0 else q_res[0]['pos']


def normalize_price(price):
    price = price.rstrip('0')
    if price[-1] == '.': price = price[:-1]
    return price


def kill_orders(secCode, comment):
    query = f"""SELECT order_id FROM public.autoorders where "SECCODE"='{secCode}' and state = 'ACTIVE' and "COMMENT"='{comment}' and order_id is not null"""
    print("kill orders:", query)
    quotes = sql.get_table.exec_query(query)
    orders = (quotes.mappings().all())
    print(orders)
    for order_num in orders:
        TransId = get_trans_id()
        orderNum = order_num['order_id']
        classCode = get_class_code(secCode)

        client_code = '' if classCode == 'SPBFUT' else '5766'
        account = 'SPBFUT002KY' if classCode == 'SPBFUT' else 'L01+00000F00'

        transaction = {
            'TRANS_ID': str(TransId),  # Номер транзакции задается клиентом
            'ACTION': 'KILL_ORDER',  # Тип заявки: Удаление существующей заявки
            'CLASSCODE': classCode,  # Код площадки
            'SECCODE': secCode,  # Код тикера
            'ORDER_KEY': str(orderNum),
            'CLIENT_CODE': client_code,
            'ACCOUNT': account
        }

        print("kill transaction sent:", transaction)
        result = qpProvider.SendTransaction(transaction)
        print("kill transaction reply:", result)
    return 0


def get_trans_id():
    return str(int((datetime.datetime.utcnow() - datetime.datetime(2023, 1, 1)).total_seconds() * 1000000) % 1000000000)


def place_order(secCode, quantity, price_bound=None, max_quantity=10, comment="mycomment", maxspread=0.0015):
    global global_reply
    global engine
    global reply

    # kill_orders(secCode, comment)
    classCode = get_class_code(secCode)
    quotes = get_quotes(classCode, secCode)[0]
    diff = get_diff(classCode, secCode)[0]

    print(f"Processing order: {secCode} {quantity} \nquotes:{quotes} \ndiff:{diff}")

    if quotes['ask'] > quotes['bid'] * (1 + maxspread):
        print(f"spread is too high: {quotes['bid']} {quotes['ask']} {quotes['ask'] / quotes['bid'] - 1}")
        return

    if (diff['bid_inc'] + diff['ask_inc']) * quantity < 0:  # classCode == 'SPBFUT' and
        print(f"price moving in opposite direction: taking pause")
        print(f"bid_inc: {diff['bid_inc']}, ask_inc:{diff['ask_inc']} quantity:{quantity}")
        return

    operation = "B" if quantity > 0 else "S"
    price = (float(quotes['ask'])) if quantity > 0 else (float(quotes['bid']))

    print(f"price {price}, price_bound {price_bound} quantity {quantity}")
    if (price_bound is not None) and (quantity * (price - price_bound) > 0):
        print(f"price {price}, price_bound {price_bound}")
        return

    price = normalize_price(str(price))
    quantity = min(max_quantity, abs(int(quantity)))

    client_code = '' if classCode == 'SPBFUT' else '5766'
    account = 'SPBFUT002KY' if classCode == 'SPBFUT' else 'L01+00000F00'

    qpProvider.OnTransReply = OnTransReply  # Ответ на транзакцию пользователя. Если транзакция выполняется из QUIK, то не вызывается
    TransId = get_trans_id()
    # https://luaq.ru/sendTransaction.html  https://euvgub.github.io/quik_user_manual/ch5_12.html
    # Новая лимитная/рыночная заявка
    transaction = {  # Все значения должны передаваться в виде строк
        'TRANS_ID': str(TransId),  # Номер транзакции задается клиентом
        'CLIENT_CODE': client_code,  # Код клиента. Для фьючерсов его нет
        'ACCOUNT': account,  # Счет
        'ACTION': 'NEW_ORDER',  # Тип заявки: Новая лимитная/рыночная заявка
        'CLASSCODE': classCode,  # Код площадки
        'SECCODE': secCode,  # Код тикера
        'OPERATION': operation,  # B = покупка, S = продажа
        'PRICE': str(price),
        # Цена исполнения. Для рыночных фьючерсных заявок наихудшая цена в зависимости от направления. Для остальных рыночных заявок цена = 0
        'QUANTITY': str(quantity),  # Кол-во в лотах
        'COMMENT': comment,
        'TYPE': 'L'}  # L = лимитная заявка (по умолчанию), M = рыночная заявка

    try:
        print("Sending transaction", transaction)
        signal.signal(signal.SIGALRM, timeout_exception)
        signal.alarm(10)
        result = qpProvider.SendTransaction(transaction)
    except Exception as e:
        print(f"error: {str(e)}")
        return
    finally:
        signal.alarm(0)

    if 'lua_error' in dict(result):
        print(f"error: {result}")
        return

    transaction['last_upd'] = datetime.datetime.now()
    order_in = pd.DataFrame([transaction])
    order_in.to_sql('orders_in', engine, if_exists='append')

    print(transaction)
    print(f'Новая лимитная/рыночная заявка отправлена на рынок:')
    print(result)

    while not reply:
        sleep(0.01)

    reply = False
    print(f"reply:{global_reply}")

    if not isinstance(global_reply['date_time'], datetime.datetime):
        global_reply['date_time'] = sqltime_to_datetime(global_reply['date_time'])
        global_reply['sent_local_time'] = sqltime_to_datetime(global_reply['sent_local_time'])
        global_reply['got_local_time'] = sqltime_to_datetime(global_reply['got_local_time'])
        global_reply['gate_reply_time'] = sqltime_to_datetime(global_reply['gate_reply_time'])

    order_out = pd.DataFrame([global_reply])
    order_out.to_sql('orders_out', engine, if_exists='append')


def place_order_tcs(secCode, quantity, price_bound=None, max_quantity=10, comment="mycomment", maxspread=0.0012):
    global engine
    global client
    global account_id

    # kill_orders(secCode, comment)
    classCode = get_class_code(secCode)
    quotes = get_quotes(classCode, secCode)[0]
    diff = get_diff(classCode, secCode)[0]

    print(quotes)
    print(diff)

    if quotes['ask'] > quotes['bid'] * (1 + maxspread):
        print(f"spread is too high: {quotes['bid']} {quotes['ask']} {quotes['ask'] / quotes['bid'] - 1}")
        return

    if (diff['bid_inc'] + diff['ask_inc']) * quantity < 0:
        print(f"price moving in opposite direction: taking pause")
        print(f"bid_inc: {diff['bid_inc']}, ask_inc:{diff['ask_inc']} quantity:{quantity}")
        return

    price = (float(quotes['ask'])) if quantity > 0 else (float(quotes['bid']))

    print(f"price {price}, price_bound {price_bound} quantity {quantity}")
    if (price_bound is not None) and (quantity * (price - price_bound) > 0):
        print(f"price out of allowed bound: price={price}, price_bound={price_bound}")
        return

    # price = normalize_price(str(price))

    figi = get_figi(secCode)
    order_id = uuid.uuid4().hex
    direction = OrderDirection.ORDER_DIRECTION_BUY if quantity > 0 else OrderDirection.ORDER_DIRECTION_SELL
    quantity = min(max_quantity, abs(int(quantity)))

    transaction = {'quantity': abs(quantity),
                   'direction': direction,
                   'account_id': account_id,
                   'order_type': OrderType.ORDER_TYPE_MARKET,
                   'order_id': order_id,
                   'instrument_id': figi
                   }

    try:
        signal.signal(signal.SIGALRM, timeout_exception)
        signal.alarm(10)
        print(transaction)
        print(f'Новая лимитная/рыночная заявка отправлена на рынок:')
        result = client.orders.post_order(**transaction)
        status = result.execution_report_status
        print("execution_report_status:", status)
        print("post_order_reply:", result)
    except Exception as e:
        print(f"error: {str(e)}")
        return
    finally:
        signal.alarm(0)

    transaction['last_upd'] = datetime.datetime.now()
    transaction['comment'] = comment
    transaction['code'] = secCode
    order_in = pd.DataFrame([transaction])
    order_in.to_sql('orders_in_tcs', engine, if_exists='append')

    res = {}
    print(result)

    def transform_money(quotation):
        try:
            if isinstance(quotation, float):
                return quotation
            else:
                return Decimal(quotation.units) + quotation.nano / Decimal("10e8")

        except Exception as ex:
            print(f"conversion error: {quotation}", str(ex))
            return Decimal(-1)

    res['order_id'] = result.order_id
    res['order_id_in'] = order_id
    res['execution_report_status'] = result.execution_report_status
    res['lots_requested'] = result.lots_requested
    res['lots_executed'] = result.lots_executed
    res['figi'] = result.figi
    res['direction'] = result.direction
    res['order_type'] = result.order_type
    res['message'] = result.message
    res['instrument_uid'] = result.instrument_uid
    res['initial_order_price'] = transform_money(result.initial_order_price)
    res['executed_order_price'] = transform_money(result.executed_order_price)
    res['total_order_amount'] = transform_money(result.total_order_amount)
    res['initial_commission'] = transform_money(result.initial_commission)
    res['executed_commission'] = transform_money(result.executed_commission)
    res['aci_value'] = transform_money(result.aci_value)
    res['initial_security_price'] = transform_money(result.initial_security_price)
    res['initial_order_price_pt'] = transform_money(result.initial_order_price_pt)
    res['code'] = secCode
    res['comment'] = comment
    order_out = pd.DataFrame([res])
    order_out.to_sql('orders_out_tcs', engine, if_exists='append')


def get_figi(ticker):
    query = f"select figi from public.tinkoff_params where ticker='{ticker}' limit 1"
    return sql.get_table.query_to_list(query)[0]['figi']


def sqltime_to_datetime(sql_time):
    return datetime.datetime(year=sql_time['year'],
                             month=sql_time['month'],
                             day=sql_time['day'],
                             hour=sql_time['hour'],
                             minute=sql_time['min'],
                             second=sql_time['sec'],
                             microsecond=sql_time['mcs']
                             )


# def set_target_position()
def get_class_code(secCode):
    query = f"select * from public.futquotes where code='{secCode}'"
    quotes = sql.get_table.exec_query(query)
    orders = (quotes.mappings().all())
    if len(orders) == 0:
        return 'TQBR'
    else:
        return 'SPBFUT'


def set_position(secCode, target_pos, sleep_time, max_amount, price_bound):
    pos = get_pos(secCode)
    print(f"pos:{pos}, target_pos:{target_pos}")

    while pos != target_pos:
        quantity = (1 if target_pos > pos else -1) * min(max_amount, abs(target_pos - pos))
        place_order(secCode, quantity, price_bound, max_amount)
        sleep(sleep_time)
        pos = get_pos(secCode)
        print(f"pos:{pos}, target_pos:{target_pos}")


def clean_open_orders():
    # all_quotes а не autoorders потому что если нет котировок - ничего не делаем
    query = "SELECT id, comment, code FROM public.allquotes where id is not null and state <> 0"
    quotes = sql.get_table.exec_query(query)
    orders = (quotes.mappings().all())

    for order in orders:
        print(f"kill open orders: {order}")
        comment = order['comment'] + str(order['id'])
        secCode = order['code']
        kill_orders(secCode, comment)  # пока так, меняет в процессе amount pending


def actualize_order_my():
    # 1)переносим сколько пендинга итд
    # 2)проставляем direction там где нет
    # 3)выключаем ордера как только ремейнс достиг quantity
    query = """
    UPDATE public.orders_my set remains=0 where remains is null;
    
    UPDATE public.orders_my as om 
    SET  remains = ag.amount, 
         pending_conf = ag.amount_pending, 
         pending_unconf = ag.unconfirmed_amount 
    FROM public.autoorders_grouped as ag
    WHERE concat(om.comment::text, om.id) = ag.comment
    and om.state <> 0 and om.provider is null; 
    
    UPDATE public.orders_my as om 
    SET  remains = ag.amount, 
         pending_conf = ag.amount_pending, 
         pending_unconf = ag.unconfirmed_amount 
    FROM public.autoorders_grouped_tcs as ag
    WHERE concat(om.comment::text, om.id) = ag.comment
    and om.state <> 0 and om.provider='tcs'; 
    
    UPDATE public.orders_my
    set direction = coalesce(direction, sign(quantity - remains))
    where state <> 0 and remains is not null; 
    UPDATE public.orders_my
    set state = 0
    where state <> 0 and direction * (quantity - remains) <= 0; 
    """
    sql.get_table.exec_query(query)


def timeout_exception():
    raise Exception("Timeout")


def process_orders(orderProcesser):
    # kill open orders by code and comment
    clean_open_orders()
    actualize_order_my()

    # как всегда allquotes потому что ничего не делаем
    query = "SELECT  * FROM public.allquotes where id is not null and direction is not null and state <> 0"

    quotes = sql.get_table.exec_query(query)
    orders = (quotes.mappings().all())

    #print(f"orders:{orders}")
    for order in orders:
        print(order)
        quantity = order['quantity'] - order['amount'] - order['amount_pending'] - order['unconfirmed_amount']

        price_bound_clause = ((order['barrier'] is not None) and (
                    quantity * (order['mid'] - order['barrier']) < 0)) or (
                                     order['barrier'] is None)
        direction_clause = ((order['direction'] * quantity) > 0)

        is_execute, secCode, quantity, price_bound, max_amount, comment = get_order_params(order)
        print(f"{secCode}\nis_barrier_ok: {price_bound_clause}\nis_direction_ok: {direction_clause}\nto_execute: {is_execute}\nqty:{quantity}\nmid:{order['mid']}\nbarrier:{order['barrier']}\n\n")

        if price_bound_clause and direction_clause and is_execute:
            # добавляем в очередь блокировки с задержкой pause
            if_not_exist = orderProcesser.add_task(
                (comment, secCode, quantity, price_bound, max_amount, comment), order['pause'])  # key 1st
            if if_not_exist:
                print("PLACING ORDER!!!")
                if order['provider'] == 'tcs':
                    place_order_tcs(secCode, quantity, price_bound, max_amount, comment)
                else:
                    place_order(secCode, quantity, price_bound, max_amount, comment)

    # get tasks tthat are scheduled
    tasks_list = orderProcesser.do_tasks()
    print(f"tasks_list:{tasks_list}")

    sleep(random.uniform(0.1, 0.3))


def get_order_params(order):
    comment = order['comment'] + str(order['id'])
    secCode = order['code']
    price_bound = order['barrier']
    quantity = order['quantity'] - order['amount'] - order['amount_pending'] - order['unconfirmed_amount']
    #logger.info(order)
    if order['order_type'] == 'flt':
        current_barrier = (order['barrier_bound'] - order['barrier']) * (order['quantity'] - quantity) / order[
            'quantity'] + order['barrier']
        logger.info(f"{secCode} executed: {order['quantity'] - quantity}")
        logger.info(f"current barrier: {current_barrier}")
        current_quantity = int(
            (order['mid'] - current_barrier) / (order['barrier_bound'] - order['barrier']) * order['quantity'])
        logger.info(f"current quantity: {current_quantity}")
        current_quantity = min(max(current_quantity, 0), quantity) if order['quantity'] > 0 else min(
            max(current_quantity, quantity), 0)
        logger.info(f"current quantity: {current_quantity}")
        # current_quantity != 0
        logger.info((current_quantity != 0, secCode, current_quantity, current_barrier, order['max_amount'], comment))
        return current_quantity != 0, secCode, current_quantity, current_barrier, order['max_amount'], comment
    elif order['order_type'] == 'trl':
        logger.info(f"{secCode} {order['direction']} minmax: {order['max_5mins'] if order['direction'] == 1 else order['min_5mins']}")
        logger.info(f"barrier_bound: {order['barrier_bound']} mid:{order['mid']}")
        if (order['direction'] == -1 and order['max_5mins'] - order['barrier_bound'] > order['mid']) \
                or (order['direction'] == 1 and order['min_5mins'] + order['barrier_bound'] < order['mid']):
            return True, secCode, quantity, price_bound, order['max_amount'], comment
        else:
            return False, secCode, quantity, price_bound, order['max_amount'], comment
    else:
        return True, secCode, quantity, price_bound, order['max_amount'], comment


if __name__ == '__main__':  # Точка входа при запуске этого скрипта
    qpProvider = QuikPy()
    orderProcesser = OrderProcesser()
    while True:
        process_orders(orderProcesser)

    qpProvider.CloseConnectionAndThread()  # Перед выходом закрываем соединение и поток QuikPy из любого экземпляра
