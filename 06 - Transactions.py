import datetime
import random
import signal
import traceback
from time import sleep
import sql.get_table
import telegram
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

from transactions import get_class_code, get_quotes, get_diff

load_dotenv(find_dotenv('my.env', True))

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

TOKEN = os.environ["TOKEN_WRITE"]
account_id = os.environ["tcs_account_id"]
client = type((Client(TOKEN))).__enter__((Client(TOKEN)))

# reply - был ли получен ответ
reply = False

# global_reply содержимое ответа - был ли получен ответ
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
        logger.info(f"Order oricessor tasks to do {tasks_to_do}")
        logger.info(f"Order oricessor tasks_list {self.tasks_list}")
        return tasks_to_do


def OnTransReply(data):
    global reply
    global global_reply
    """Обработчик события ответа на транзакцию пользователя"""
    global_reply = data['data']
    reply = True


def OnOrder(data):
    """Обработчик события получения новой / изменения существующей заявки"""
    logger.info(f"OnOrder: {data['data']}")


def OnTrade(data):
    """Обработчик события получения новой / изменения существующей сделки
    Не вызывается при закрытии сделки
    """
    logger.info(f"OnTrade: {data['data']}")


def OnFuturesClientHolding(data):
    """Обработчик события изменения позиции по срочному рынку"""
    logger.info(f"OnFuturesClientHolding: {data['data']}")


def OnDepoLimit(data):
    """Обработчик события изменения позиции по инструментам"""
    logger.info(f"OnDepoLimit: {data['data']}")


def OnDepoLimitDelete(data):
    """Обработчик события удаления позиции по инструментам"""
    logger.info(f"OnDepoLimitDelete: {data['data']}")


def normalize_price(price):
    price = price.rstrip('0')
    if price[-1] == '.': price = price[:-1]
    return price


def kill_orders(secCode, comment):
    query = f"""SELECT order_id FROM public.autoorders 
    where "SECCODE"='{secCode}' and state = 'ACTIVE' and "COMMENT"='{comment}' and order_id is not null
    """
    orders = sql.get_table.query_to_list(query)

    logger.info(f"kill orders: {orders}")

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

        logger.info(f"kill transaction sent: \n{transaction}")
        result = qpProvider.SendTransaction(transaction)
        logger.info(f"reply: \n{result}")


def get_trans_id():
    return str(int((datetime.datetime.utcnow() - datetime.datetime(2023, 1, 1)).total_seconds() * 1000000) % 1000000000)


def place_order(secCode, quantity, price_bound=None, max_quantity=10, comment="mycomment", maxspread=0.0015):
    """
    maxspread - отношения бида к аску при котором сделаем сделку
    """
    global global_reply
    global engine
    global reply

    classCode = get_class_code(secCode)
    quotes = get_quotes(classCode, secCode)[0]
    diff = get_diff(classCode, secCode)[0]

    logger.info(f"Processing order: {secCode} {quantity} \nquotes:{quotes} \ndiff:{diff}")

    if quotes['ask'] > quotes['bid'] * (1 + maxspread):
        logger.info(f"spread is too high: {quotes['bid']} {quotes['ask']} {quotes['ask'] / quotes['bid'] - 1}")
        return

    if (diff['bid_inc'] + diff['ask_inc']) * quantity < 0:  # classCode == 'SPBFUT' and
        logger.info(f"price moving in opposite direction: taking pause")
        logger.info(f"bid_inc: {diff['bid_inc']}, ask_inc:{diff['ask_inc']} quantity:{quantity}")
        return

    operation = "B" if quantity > 0 else "S"
    price = (float(quotes['ask'])) if quantity > 0 else (float(quotes['bid']))

    logger.info(f"price {price}, price_bound {price_bound} quantity {quantity}")
    if (price_bound is not None) and (quantity * (price - price_bound) > 0):
        logger.info(f"PriceVound fail: price {price}, price_bound {price_bound}, quantity {quantity}")
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
        logger.info(f"Sending transaction: \n{transaction}")
        signal.signal(signal.SIGALRM, timeout_exception)
        signal.alarm(10)
        result = qpProvider.SendTransaction(transaction)
    except Exception as e:
        msg = traceback.format_exc()
        logger.error(msg)
        telegram.send_message(msg, True)
        return
    finally:
        signal.alarm(0)

    if 'lua_error' in dict(result):
        logger.error(f"error: {result}")
        return

    transaction['last_upd'] = datetime.datetime.now()
    order_in = pd.DataFrame([transaction])
    order_in.to_sql('orders_in', engine, if_exists='append')

    logger.info(f'Заявка отправлена:\n{transaction} \n\nПолучен ответ:\n{result}')

    while not reply:
        sleep(0.01)

    reply = False
    logger.info(f"reply:{global_reply}")

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


def clean_open_orders():
    # all_quotes а не autoorders потому что если нет котировок - ничего не делаем
    query = "SELECT id, comment, code FROM public.allquotes where id is not null and state <> 0"
    orders = sql.get_table.query_to_list(query)

    for order in orders:
        logger.info(f"kill open orders: {order}")
        comment = f"{order['comment']}{order['id']}"
        kill_orders(order['code'], comment)  # пока так, меняет в процессе amount pending


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
    set direction = sign(quantity - remains)
    where state <> 0 and remains is not null and direction is null; 
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
    orders = sql.get_table.query_to_list(query)

    # print(f"orders:{orders}")
    for order in orders:
        logger.info(order)
        quantity = order['quantity'] - order['amount'] - order['amount_pending'] - order['unconfirmed_amount']

        price_bound_clause = (order['barrier'] is None) or ((order['barrier'] is not None)
                                                            and (quantity * (order['mid'] - order['barrier']) < 0))

        direction_clause = ((order['direction'] * quantity) > 0)

        is_execute, secCode, quantity, price_bound, max_amount, comment = get_order_params(order)
        logger.info(
            f"{secCode}\nis_barrier_ok: {price_bound_clause}\n"
            f"is_direction_ok: {direction_clause}\n"
            f"to_execute: {is_execute}\n"
            f"qty:{quantity}\n"
            f"mid:{order['mid']}\n"
            f"barrier:{order['barrier']}\n\n")

        if price_bound_clause and direction_clause and is_execute:
            # добавляем в очередь блокировки с задержкой pause
            if_not_exist = orderProcesser.add_task(
                (comment, secCode, quantity, price_bound, max_amount, comment), order['pause'])  # key 1st
            if if_not_exist:

                if order['provider'] == 'tcs':
                    logger.info("PLACING ORDER TCS")
                    place_order_tcs(secCode, quantity, price_bound, max_amount, comment)
                else:
                    logger.info("PLACING ORDER PSB")
                    place_order(secCode, quantity, price_bound, max_amount, comment)

    tasks_list = orderProcesser.do_tasks()
    logger.info(f"tasks_list:{tasks_list}")

    sleep(random.uniform(0.1, 0.2))


def get_order_params(order):
    comment = order['comment'] + str(order['id'])
    secCode = order['code']
    price_bound = order['barrier']
    quantity = order['quantity'] - order['amount'] - order['amount_pending'] - order['unconfirmed_amount']
    # logger.info(order)
    if order['order_type'] == 'flt':
        current_barrier = ((order['barrier_bound'] - order['barrier'])
                           * (order['quantity'] - quantity) / order['quantity'] + order['barrier'])
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
        logger.info(
            f"{secCode} {order['direction']} minmax: {order['max_5mins'] if order['direction'] == 1 else order['min_5mins']}")
        logger.info(f"barrier_bound: {order['barrier_bound']} mid:{order['mid']}")
        if (order['direction'] == -1 and order['max_5mins'] - order['barrier_bound'] > order['mid']) \
                or (order['direction'] == 1 and order['min_5mins'] + order['barrier_bound'] < order['mid']):
            return True, secCode, quantity, price_bound, order['max_amount'], comment
        else:
            return False, secCode, quantity, price_bound, order['max_amount'], comment
    else:
        return True, secCode, quantity, price_bound, order['max_amount'], comment


def get_order_params_v2(order):
    # Генерация уникального комментария для заказа
    comment = f"{order['comment']}{order['id']}"
    secCode = order['code']
    price_bound = order['barrier']
    # Вычисление оставшегося количества на основе текущих данных
    quantity = order['quantity'] - (order['amount'] + order['amount_pending'] + order['unconfirmed_amount'])

    # Обработка заказов типа 'flt' (floating type)
    if order['order_type'] == 'flt':
        # Вычисление текущего барьера с учетом изменений количества
        current_barrier = ((order['barrier_bound'] - order['barrier']) *
                           (order['quantity'] - quantity) / order['quantity'] + order['barrier'])
        logger.info(f"{secCode} executed: {order['quantity'] - quantity}")
        logger.info(f"current barrier: {current_barrier}")

        # Вычисление текущего количества на основе средней цены и текущего барьера
        current_quantity = int((order['mid'] - current_barrier) /
                               (order['barrier_bound'] - order['barrier']) * order['quantity'])
        logger.info(f"current quantity: {current_quantity}")

        # Корректировка текущего количества на основе максимальных и минимальных значений
        current_quantity = min(max(current_quantity, 0), quantity) if order['quantity'] > 0 else min(
            max(current_quantity, quantity), 0)
        logger.info(f"current quantity: {current_quantity}")

        # Возвращаем результаты для заказов типа 'flt'
        return current_quantity != 0, secCode, current_quantity, current_barrier, order['max_amount'], comment

    # Обработка заказов типа 'trl' (trailing type)
    elif order['order_type'] == 'trl':
        logger.info(
            f"{secCode} {order['direction']} minmax: {order['max_5mins'] if order['direction'] == 1 else order['min_5mins']}")
        logger.info(f"barrier_bound: {order['barrier_bound']} mid:{order['mid']}")

        # Проверка условий для активации трейлинг ордера
        if (order['direction'] == -1 and order['max_5mins'] - order['barrier_bound'] > order['mid']) \
                or (order['direction'] == 1 and order['min_5mins'] + order['barrier_bound'] < order['mid']):
            return True, secCode, quantity, price_bound, order['max_amount'], comment
        else:
            return False, secCode, quantity, price_bound, order['max_amount'], comment

    # Возвращаем дефолтные значения для остальных случаев
    else:
        return True, secCode, quantity, price_bound, order['max_amount'], comment


if __name__ == '__main__':  # Точка входа при запуске этого скрипта
    qpProvider = QuikPy()
    orderProcesser = OrderProcesser()
    while True:
        process_orders(orderProcesser)

    # qpProvider.CloseConnectionAndThread()  # Перед выходом закрываем соединение и поток QuikPy из любого экземпляра
