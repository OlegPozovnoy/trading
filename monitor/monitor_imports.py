import datetime

import telegram_send
import asyncio
import sql.get_table
from datetime import datetime, timedelta
from tools.utils import sync_timed


def monitor_import(check_sec, check_fut, check_tinkoff):
    if check_sec: check_sec_tables()
    if check_fut: check_futures_tables()
    if check_tinkoff: check_quotes_import_5min()


def check_sec_tables():
    check_last_upd("secquotesdiff")
    check_quotes_import_emptytable(['pos_eq', 'pos_collat'])
    check_quotes_doubling('secquotes')
    check_quotes_import_money('TQBR')


def check_futures_tables():
    check_last_upd("futquotesdiff")
    check_quotes_import_emptytable(['pos_fut', 'pos_money'])
    check_quotes_doubling('futquotes')
    check_quotes_import_money('SPBFUT')


#@sync_timed()
def check_last_upd(table_name):
    query = f"select max(last_upd) from public.{table_name};"
    try:
        last_upd = sql.get_table.query_to_list(query)[0]['max'].replace(tzinfo=None)
        msg = f"{table_name} last_upd: {last_upd} < time_bound: {datetime.now() - timedelta(minutes=10)}"
        if last_upd < datetime.now() - timedelta(minutes=10):
            asyncio.run(telegram_send.send_message(msg, urgent=True))
    except:
        asyncio.run(telegram_send.send_message(f"quotes import: 0 records in {table_name}", urgent=True))


#@sync_timed()
def check_quotes_import_emptytable(tables) -> None:
    """
    check 'pos_fut', 'pos_money', 'pos_eq', 'pos_collat' are not empty
    :return: None
    """
    for table in tables:
        query = f"select count(*) as cnt from public.{table}"
        cnt = sql.get_table.query_to_list(query)[0]['cnt']
        if int(cnt) == 0:
            asyncio.run(telegram_send.send_message(f"table {table} is empty", urgent=True))


#@sync_timed()
def check_quotes_import_money(board) -> None:
    """
    check pos_money(free money spbfut), pos_collat (free collateral tqbr) tables
    :return: None
    """
    # check that money are imported
    query = f"SELECT count(*) as cnt_rows, count(money) as cnt_money FROM public.money where board='{board}';"
    try:
        res = sql.get_table.query_to_list(query)[0]
        cnt_rows = res['cnt_rows']
        cnt_money = res['cnt_money']
        if (cnt_rows, cnt_money) != (1, 1):
            msg = f"table public.money board {board} error: (cnt_rows, cnt_money)={(cnt_rows, cnt_money)}"
            asyncio.run(telegram_send.send_message(msg, urgent=True))
    except:
        msg = f"table public.money board {board} error: no records returned"
        asyncio.run(telegram_send.send_message(msg, urgent=True))


#@sync_timed()
def check_quotes_doubling(table_name):
    query = f"select code from {table_name} group by code having count(*) >= 2;"

    doubled_list = sql.get_table.query_to_list(query)
    if len(doubled_list) != 0:
        asyncio.run(telegram_send.send_message(f"quotes {table_name} doubling: {doubled_list}", urgent=True))


#@sync_timed()
def check_quotes_import_5min() -> None:
    """
    checks there are rows in df_all_candles_t for the last 5 mins
    :return:
    """
    query_candles = "SELECT count(*) as cnt from  df_all_candles_t where datetime > now() - interval '5 minutes'"
    cnt_rows = sql.get_table.query_to_list(query_candles)[0]['cnt']
    if cnt_rows == 0:
        asyncio.run(
            telegram_send.send_message(f"tinkoff candles import error: no candles in df_all_candles_t for the last 5 mins",
                                  urgent=True))




