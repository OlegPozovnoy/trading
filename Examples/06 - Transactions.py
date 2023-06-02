import datetime
import os
import random
import sys
from time import sleep
import sql.get_table
from QuikPy.QuikPy import QuikPy  # Работа с QUIK из Python через LUA скрипты QuikSharp
from decimal import Decimal
import pandas as pd

reply = False
global_reply = None
engine = sql.get_table.engine


class OrderProcesser():
    def __init__(self):
        self.tasks_list = []

    def add_task(self,task, timeout):
        if task[0] not in [item[0][0] for item in self.tasks_list]: #item[0] order item[0][0] - key
            self.tasks_list.append((task, datetime.datetime.now() + datetime.timedelta(seconds=timeout)))
            self.tasks_list = sorted(self.tasks_list, key=lambda x: x[1])
            return True # task is scheduled
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
        query = f"""SELECT * FROM public.secquotes where code='{secCode}' LIMIT 1"""
    quotes = sql.get_table.exec_query(query)
    return quotes.mappings().all()


def get_pos(secCode):
    query = f"""SELECT * FROM public.united_pos where code='{secCode}' LIMIT 1"""
    print(query)
    quotes = sql.get_table.exec_query(query)
    q_res = quotes.mappings().all()
    print(quotes.mappings().all())
    if len(q_res) == 0:
        res = 0
    else:
        res = q_res[0]['pos']
    return res


def normalize_price(price):
    price = price.rstrip('0')
    if price[-1] == '.': price = price[:-1]
    return price


def kill_orders(secCode, comment):
    query = f"""SELECT order_num FROM public.autoorders where "SECCODE"='{secCode}' and state = 'ACTIVE' and "COMMENT"='{comment}'"""
    print(query)
    quotes = sql.get_table.exec_query(query)
    orders = (quotes.mappings().all())
    print(orders)
    for order_num in orders:
        TransId = get_trans_id()
        orderNum = order_num['order_num']
        classCode = get_class_code(secCode)

        transaction = {
            'TRANS_ID': str(TransId),  # Номер транзакции задается клиентом
            'ACTION': 'KILL_ORDER',  # Тип заявки: Удаление существующей заявки
            'CLASSCODE': classCode,  # Код площадки
            'SECCODE': secCode,  # Код тикера
            'ORDER_KEY': str(orderNum)}

        print(transaction)
        result = qpProvider.SendTransaction(transaction)
        print(result)
    return 0


def get_trans_id():
    return str(int((datetime.datetime.utcnow() - datetime.datetime(2023, 1, 1)).total_seconds() * 1000000) % 1000000000)


def place_order(secCode, quantity, price_bound=None, max_quantity=10, comment="mycomment", maxspread=0.0004, is_fast=False):
    global global_reply
    global engine
    global reply

    kill_orders(secCode, comment)
    classCode=get_class_code(secCode)
    quotes = get_quotes(classCode, secCode)[0]
    diff = get_diff(classCode, secCode)[0]

    print(quotes)
    print(diff)

    if quotes['ask'] > quotes['bid'] * (1 + maxspread):
        print(f"spread is too high: {quotes['bid']} {quotes['ask']} {quotes['ask'] / quotes['bid'] - 1}")
        return

    if classCode == 'SPBFUT' and (diff['bid_inc'] + diff['ask_inc']) * quantity < 0:
        print(f"price moving in opposite direction: taking pause")
        print(f"bid_inc: {diff['bid_inc']}, ask_inc:{diff['ask_inc']} quantity:{quantity}")
        return

    operation = "B" if quantity > 0 else "S"
    price = (float(quotes['ask'])) if quantity > 0 else (float(quotes['bid']))

    print(f"price {price}, price_bound {price_bound} quantity{quantity}")
    if (price_bound is not None) and (quantity * (price - price_bound) > 0):
        print(f"price {price}, price_bound {price_bound}")
        return

    if is_fast:
        quantity=1


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
        result = qpProvider.SendTransaction(transaction)
    except Exception as e:
        print(f"error: {str(e)}")
        return
    if 'lua_error' in dict(result):
        print(f"error: {result}")
        return

    transaction['last_upd'] = datetime.datetime.now()
    order_in = pd.DataFrame([transaction])
    order_in.to_sql('orders_in', engine, if_exists='append')

    print(transaction)
    print(f'Новая лимитная/рыночная заявка отправлена на рынок:')
    print(result)
    print(result["data"])

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
    print(query)
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


def dummyfunc(args):
    secCode, quantity, price_bound, max_quantity,  comment = args
    place_order(secCode, quantity, price_bound, max_quantity, comment)


def process_orders(orderProcesser):
    query = "SELECT  * FROM public.allquotes where id is not null and amount + amount_pending + unconfirmed_amount <> quantity and state <> 0"

    quotes = sql.get_table.exec_query(query)
    orders = (quotes.mappings().all())

    print(f"orders:{orders}")
    for order in orders:
        print(order)
        comment = order['comment'] + str(order['id'])
        secCode = order['code']
        kill_orders(secCode, comment)
        price_bound=order['barrier']
        quantity=order['quantity']-order['amount']

        if ((price_bound is not None) and (quantity * (order['mid'] - price_bound) < 0)) or (price_bound is None):
            if_not_exist = orderProcesser.add_task((comment, secCode, quantity, price_bound, order['max_amount'], comment), order['pause'])  # key 1st
            if if_not_exist:
                place_order(secCode, quantity, price_bound, order['max_amount'], comment)

        update_query = f"update public.orders_my set remains = {order['amount'] + order['amount_pending'] + order['unconfirmed_amount']} where id = {order['id']}"
        sql.get_table.exec_query(update_query)

        update_query = f"update public.orders_my set state = 0  where id = {order['id']} and remains = quantity"
        sql.get_table.exec_query(update_query)

        sleep(0.1)

    # get tasks tthat are scheduled
    tasks_list = orderProcesser.do_tasks()
    print(f"tasks_list:{tasks_list}")
    for task in tasks_list:
        print(f"processing taks {task}")
        place_order(task[0][1], task[0][2], task[0][3], task[0][4], task[0][5])

    sleep(random.uniform(0,0.1))




if __name__ == '__main__':  # Точка входа при запуске этого скрипта
    #print("!!!!",os.getcwd())

    qpProvider = QuikPy()
    orderProcesser = OrderProcesser()
    while True:
        process_orders(orderProcesser)
    #set_position('VTBR', 0, sleep_time=10, max_amount=100000, price_bound=None)

    qpProvider.CloseConnectionAndThread()  # Перед выходом закрываем соединение и поток QuikPy из любого экземпляра






















# Удаление существующей лимитной заявки
# orderNum =   # 19-и значный номер заявки
# transaction = {
#    'TRANS_ID': str(TransId),  # Номер транзакции задается клиентом
#    'ACTION': 'KILL_ORDER',  # Тип заявки: Удаление существующей заявки
#    'CLASSCODE': classCode,  # Код площадки
#    'SECCODE': secCode,  # Код тикера
#     'ORDER_KEY': str(orderNum)
# }  # Номер заявки
# print(f'Удаление заявки отправлено на рынок: {qpProvider.SendTransaction(transaction)["data"]}')

# while reply == False:
#    sleep(0.01)
# Новая стоп заявка
# StopSteps = 10  # Размер проскальзывания в шагах цены
# slippage = float(qpProvider.GetSecurityInfo(classCode, secCode)['data']['min_price_step']) * StopSteps  # Размер проскальзывания в деньгах
# if slippage.is_integer():  # Целое значение проскальзывания мы должны отправлять без десятичных знаков
#    slippage = int(slippage)  # поэтому, приводим такое проскальзывание к целому числу
# transaction = {  # Все значения должны передаваться в виде строк
#    'TRANS_ID': str(TransId),  # Номер транзакции задается клиентом
#    'CLIENT_CODE': '',  # Код клиента. Для фьючерсов его нет
#    'ACCOUNT': 'SPBFUT00PST',  # Счет
#    'ACTION': 'NEW_STOP_ORDER',  # Тип заявки: Новая стоп заявка
#    'CLASSCODE': classCode,  # Код площадки
#    'SECCODE': secCode,  # Код тикера
#    'OPERATION': 'B',  # B = покупка, S = продажа
#    'PRICE': str(price),  # Цена исполнения
#    'QUANTITY': str(quantity),  # Кол-во в лотах
#    'STOPPRICE': str(price + slippage),  # Стоп цена исполнения
#    'EXPIRY_DATE': 'GTC'}  # Срок действия до отмены
# print(f'Новая стоп заявка отправлена на рынок: {qpProvider.SendTransaction(transaction)["data"]}')

# Удаление существующей стоп заявки
# orderNum = 1234567  # Номер заявки
# transaction = {
#     'TRANS_ID': str(TransId),  # Номер транзакции задается клиентом
#     'ACTION': 'KILL_STOP_ORDER',  # Тип заявки: Удаление существующей заявки
#     'CLASSCODE': classCode,  # Код площадки
#     'SECCODE': secCode,  # Код тикера
#     'STOP_ORDER_KEY': str(orderNum)}  # Номер заявки
# print(f'Удаление стоп заявки отправлено на рынок: {qpProvider.SendTransaction(transaction)["data"]}')

    # qpProvider = QuikPy()  # Вызываем конструктор QuikPy с подключением к локальному компьютеру с QUIK
    # qpProvider = QuikPy(Host='<Ваш IP адрес>')  # Вызываем конструктор QuikPy с подключением к удаленному компьютеру с QUIK
    # qpProvider.OnOrder = OnOrder  # Получение новой / изменение существующей заявки
    # qpProvider.OnTrade = OnTrade  # Получение новой / изменение существующей сделки
    # qpProvider.OnFuturesClientHolding = OnFuturesClientHolding  # Изменение позиции по срочному рынку
    # qpProvider.OnDepoLimit = OnDepoLimit  # Изменение позиции по инструментам
    # qpProvider.OnDepoLimitDelete = OnDepoLimitDelete  # Удаление позиции по инструментам

    # Вызываем конструктор QuikPy с подключением к локальному компьютеру с QUIK
    # qpProvider = QuikPy(Host='<Ваш IP адрес>')  # Вызываем конструктор QuikPy с подключением к удаленному компьютеру с QUIK
#«NEW_ORDER» – новая заявка,
#«NEW_STOP_ORDER» – новая стоп-заявка,
#«KILL_ORDER» – снять заявку,
#«KILL_STOP_ORDER» – снять стоп-заявку,
#«KILL_ALL_ORDERS» – снять все заявки из торговой системы,
#«KILL_ALL_STOP_ORDERS» – снять все стоп-заявки,
#«KILL_ALL_FUTURES_ORDERS» – снять все заявки на рынке FORTS,
#«MOVE_ORDERS» – переставить заявки на рынке FORTS,
#«NEW_QUOTE» – новая безадресная заявка,
#«KILL_QUOTE» – снять безадресную заявку,
