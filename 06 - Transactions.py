import datetime
import random
import signal
import traceback
from time import sleep
import sql.get_table
import telegram_send
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

from tools.utils import sync_timed
from transactions import get_class_code, get_quotes, get_diff

load_dotenv(find_dotenv('my.env', True))

logger = logging.getLogger(__name__)
logging.basicConfig(filename='./logs/transactions.log', filemode='a', level=logging.INFO)

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
        logger.info(f"Tasks to do now: {tasks_to_do}")
        logger.info(f"Tasks list: {self.tasks_list}")
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


def normalize_price_psb(price):
    price = price.rstrip('0')
    if price[-1] == '.': price = price[:-1]
    return price


@sync_timed()
def kill_orders(secCode, comment):
    query = f"""SELECT order_id FROM public.autoorders 
    where "SECCODE"='{secCode}' and state = 'ACTIVE' and "COMMENT"='{comment}' and order_id is not null
    """
    orders = sql.get_table.query_to_list(query)

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

        logger.info(f"Sent KILL_ORDER: \n{transaction}")
        result = qpProvider.SendTransaction(transaction)
        logger.info(f"got KILL_ORDER reply: \n{result}")


def get_trans_id():
    return str(int((datetime.datetime.utcnow() - datetime.datetime(2023, 1, 1)).total_seconds() * 1000000) % 1000000000)


def check_order_validity(quotes: dict, diff: dict, quantity: int, barrier: float, maxspread: float) -> bool:
    if quotes['ask'] > quotes['bid'] * (1 + maxspread):
        logger.warning(
            f"spread is too high: {quotes['bid']}-{quotes['ask']} {(quotes['ask'] / quotes['bid'] - 1) * 100}prct")
        return False

    if (diff['bid_inc'] + diff['ask_inc']) * quantity < 0:  # classCode == 'SPBFUT' and
        logger.warning(f"price moving in opposite direction: taking pause")
        logger.warning(f"bid_inc: {diff['bid_inc']}, ask_inc:{diff['ask_inc']} quantity:{quantity}")
        return False

    price = (float(quotes['ask'])) if quantity > 0 else (float(quotes['bid']))

    logger.info(f"Barrier check: {price=}, {barrier=} {quantity=}")
    if (barrier is not None) and (quantity * (price - barrier) > 0):
        logger.warning("Barrier check FAIL")
        return False

    return True


def get_order_features(secCode):
    classCode = get_class_code(secCode)
    quotes = get_quotes(classCode, secCode)[0]
    diff = get_diff(classCode, secCode)[0]
    return classCode, quotes, diff


@sync_timed()
def place_order(secCode, quantity, price_bound=None, max_quantity=10, comment="mycomment", maxspread=0.0015):
    """
    maxspread - отношения бида к аску при котором сделаем сделку
    """
    global global_reply
    global engine
    global reply

    classCode, quotes, diff = get_order_features(secCode)

    if classCode == 'SPBFUT':
        money = quotes['collateral']
    else:
        money = quotes['ask'] * quotes['lot']

    logger.warning(f"Processing order: {secCode} {quantity} \nquotes:{quotes} \ndiff:{diff}")

    if not check_order_validity(quotes, diff, quantity, price_bound, maxspread):
        return

    operation = "B" if quantity > 0 else "S"
    price = (float(quotes['ask'])) if quantity > 0 else (float(quotes['bid']))
    price = normalize_price_psb(str(price))
    quantity = min(max_quantity, abs(int(quantity)))

    qpProvider.OnTransReply = OnTransReply  # Ответ на транзакцию пользователя. Если транзакция выполняется из QUIK, то не вызывается

    # https://luaq.ru/sendTransaction.html  https://euvgub.github.io/quik_user_manual/ch5_12.html
    # Все значения должны передаваться в виде строк
    transaction = {
        'TRANS_ID': str(get_trans_id()),  # Номер транзакции задается клиентом
        'CLIENT_CODE': '' if classCode == 'SPBFUT' else '5766',  # Код клиента. Для фьючерсов его нет
        'ACCOUNT': 'SPBFUT002KY' if classCode == 'SPBFUT' else 'L01+00000F00',  # Счет
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
        telegram_send.send_message(msg, True)
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
        sleep(0.001)

    reply = False
    logger.info(f"reply:{global_reply}")

    if not isinstance(global_reply['date_time'], datetime.datetime):
        global_reply['date_time'] = sqltime_to_datetime(global_reply['date_time'])
        global_reply['sent_local_time'] = sqltime_to_datetime(global_reply['sent_local_time'])
        global_reply['got_local_time'] = sqltime_to_datetime(global_reply['got_local_time'])
        global_reply['gate_reply_time'] = sqltime_to_datetime(global_reply['gate_reply_time'])

    order_out = pd.DataFrame([global_reply])
    order_out.to_sql('orders_out', engine, if_exists='append')


@sync_timed()
def place_order_tcs(secCode, quantity, price_bound=None, max_quantity=10, comment="mycomment", maxspread=0.0012):
    global engine
    global client
    global account_id

    # kill_orders(secCode, comment)
    classCode, quotes, diff = get_order_features(secCode)

    if classCode == 'SPBFUT':
        money = quotes['collateral']
    else:
        money = quotes['ask'] * quotes['lot']

    if not check_order_validity(quotes, diff, quantity, price_bound, maxspread):
        return

    order_id = uuid.uuid4().hex
    transaction = {'quantity': min(max_quantity, abs(int(quantity))),
                   'direction': OrderDirection.ORDER_DIRECTION_BUY if quantity > 0 else OrderDirection.ORDER_DIRECTION_SELL,
                   'account_id': account_id,
                   'order_type': OrderType.ORDER_TYPE_MARKET,
                   'order_id': order_id,
                   'instrument_id': get_figi(secCode)
                   }

    try:
        signal.signal(signal.SIGALRM, timeout_exception)
        signal.alarm(10)
        logger.warning(f'Новая лимитная/рыночная заявка отправлена на рынок:{transaction}')
        result = client.orders.post_order(**transaction)
        status = result.execution_report_status
        logger.warning(f"execution_report_status: {status}")
        logger.warning(f"post_order_reply: {result}")
    except Exception as e:
        logger.error(f"error: {str(e)}")
        return
    finally:
        signal.alarm(0)

    transaction['last_upd'] = datetime.datetime.now()
    transaction['comment'] = comment
    transaction['code'] = secCode
    order_in = pd.DataFrame([transaction])
    order_in.to_sql('orders_in_tcs', engine, if_exists='append')

    res = {}

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


@sync_timed()
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


@sync_timed()
def clean_open_orders():
    """
    получаем список всех открытых ордеров и отправляем сигнал kill
    all_quotes а не autoorders потому что если нет котировок - ничего не делаем
    :return:
    """
    query = "SELECT id, comment, code FROM public.allquotes where id is not null and state <> 0 and provider <> 'tcs'"
    orders = sql.get_table.query_to_list(query)

    for order in orders:
        logger.info(f"kill open orders: {order}")
        comment = f"{order['comment']}{order['id']}"
        kill_orders(order['code'], comment)  # пока так, меняет в процессе amount pending


@sync_timed()
def actualize_order_my():
    """
    1)переносим сколько пендинга итд
    2)проставляем direction там где нет
    3)выключаем ордера как только ремейнс достиг quantity
    :return:
    """
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


@sync_timed()
def process_orders(orderProcesser):
    clean_open_orders()
    actualize_order_my()

    # как всегда allquotes потому что ничего не делаем когда рынок закрыт
    query = "SELECT  * FROM public.allquotes where id is not null and direction is not null and state <> 0"
    orders = sql.get_table.query_to_list(query)

    for order in orders:
        logger.info(order)
        quantity = order['quantity'] - order['amount'] - order['amount_pending'] - order['unconfirmed_amount']

        price_bound_clause = (order['barrier'] is None) or ((order['barrier'] is not None)
                                                            and (quantity * (order['mid'] - order['barrier']) < 0))

        direction_clause = ((order['direction'] * quantity) > 0)

        is_execute, secCode, quantity, price_bound, max_amount, comment = get_order_params(order)
        logger.info(f"""ORDER: {secCode=}
            {quantity=} {direction_clause=}
            price {order['mid']} vs {order['barrier']} barrier: {price_bound_clause=}
            {is_execute=}""")

        if price_bound_clause and direction_clause and is_execute:
            # добавляем в очередь блокировки с задержкой pause
            if_not_exist = orderProcesser.add_task(
                (comment, secCode, quantity, price_bound, max_amount, comment), order['pause'])  # key 1st
            if if_not_exist:
                if order['provider'] == 'tcs':
                    logger.warning(
                        f"ORDER TCS {datetime.datetime.now()} {secCode=} {quantity=} {price_bound=} {max_amount=} {comment=}")
                    place_order_tcs(secCode, quantity, price_bound, max_amount, comment)
                else:
                    logger.warning(
                        f"ORDER PSB {datetime.datetime.now()} {secCode=} {quantity=} {price_bound=} {max_amount=} {comment=}")
                    place_order(secCode, quantity, price_bound, max_amount, comment)

    tasks_list = orderProcesser.do_tasks()
    logger.info(f"tasks_list:{tasks_list}")
    sleep(random.uniform(0.05, 0.1))


def get_order_params(order):
    comment = order['comment'] + str(order['id'])
    secCode = order['code']
    price_bound = order['barrier']

    # сколько осталось купить
    remaining_quantity = order['quantity'] - order['amount'] - order['amount_pending'] - order['unconfirmed_amount']
    executed_quantity = order['amount'] + order['amount_pending'] + order['unconfirmed_amount']

    if order['order_type'] == 'flt':
        # считаем новое значение барьера, он сдвинется пропорционально части исполненного ордера от order['barrier'] к order['barrier_bound']
        barrier_out = ((order['barrier_bound'] - order['barrier'])
                       * executed_quantity / order['quantity'] + order['barrier'])

        # считаем, сколько можем исполнить по текущей цене исходя из нового значения барьера
        current_quantity = int(
            order['quantity'] * (order['mid'] - barrier_out) / (order['barrier_bound'] - order['barrier']))

        logger.info(f"""{secCode} executed: {executed_quantity} out of {order['quantity']}")
        BARRIERS: {order['barrier']}-{barrier_out}-{order['barrier_bound']}
        {current_quantity=} {remaining_quantity=}""")

        # и надо проследить, что что-бы мы не посчитали, при покупке получим что-то в отрезке [0, remaining_quantity]
        # при продаже [remaining_quantity, 0]
        if order['quantity'] > 0:
            quantity_out = min(max(current_quantity, 0), remaining_quantity)
        else:
            quantity_out = min(max(current_quantity, remaining_quantity), 0)
        is_execute = (quantity_out != 0)
    elif order['order_type'] == 'trl':
        # мы продадим если цена уже упала от максимума: например гэп вверх и мы говорим что начнем продавать когда снизится от максимума на рубль
        quantity_out = remaining_quantity
        barrier_out = order['barrier']

        logger.info(
            f"""ORDER TYPE: TRAILING - {secCode=} {order['direction']} 
            minmax: {order['max_5mins'] if order['direction'] == 1 else order['min_5mins']}
            price:{order['mid']}
            barrier_bound: {order['barrier_bound']}""")

        if order['direction'] == 1 and order['mid'] - order['min_5mins'] > order['barrier_bound']:
            is_execute = True
        elif order['direction'] == -1 and order['max_5mins'] - order['mid'] > order['barrier_bound']:
            is_execute = True
        else:
            is_execute = False
    else:
        quantity_out = remaining_quantity
        barrier_out = order['barrier']
        is_execute = True

    logger.info(
        f"get_order_params returnrf :{is_execute=}, {secCode=}, {quantity_out=}, {barrier_out=}, {order['max_amount']}, {comment}")
    return is_execute, secCode, quantity_out, barrier_out, order['max_amount'], comment


if __name__ == '__main__':  # Точка входа при запуске этого скрипта
    qpProvider = QuikPy()
    orderProcesser = OrderProcesser()
    while True:
        process_orders(orderProcesser)

    # qpProvider.CloseConnectionAndThread()  # Перед выходом закрываем соединение и поток QuikPy из любого экземпляра
