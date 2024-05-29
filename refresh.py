import asyncio
import os
import traceback

import pytz
from numba import njit

import sql.get_table
import sql.async_exec
import time
import datetime
import logging
import sys

import telegram_send
import tools.clean_processes
from refresh.orders_state import update_orders_state
from refresh.queries import get_query_fut_upd, get_query_sec_upd, get_query_signals_upd, get_query_store_jump_events, \
    get_query_deact_by_endtime, get_query_bidask_upd, get_query_events_update_news, get_query_events_update_jumps, \
    get_query_events_update_prices, get_remove_sec_duplicates, get_remove_fut_duplicates
from tools import compose_td_datetime
from tools.utils import sync_timed

logger = logging.getLogger()
logger.setLevel(logging.INFO)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


@sync_timed()
def log_timing():
    query_fut = f"select max(updated_at), count(*), '{datetime.datetime.now()}' as cnt from public.futquotesdiff;"
    query_sec = f"select max(updated_at), count(*), '{datetime.datetime.now()}' as cnt from public.secquotesdiff;"

    last_sec = sql.get_table.query_to_list(query_sec)[0]
    last_fut = sql.get_table.query_to_list(query_fut)[0]
    logger.info(f"\nsec: {last_sec}\nfut: {last_fut}")


def process_error():
    error_msg = f"Error in quotes upd: {traceback.format_exc()}"
    telegram_send.send_message(error_msg, True)
    logger.error(error_msg)


@sync_timed()
def market_data_upd(sequential=True):
    current_time = datetime.datetime.now(moscow_tz).isoformat()

    sql_query_list = [
        get_query_fut_upd(current_time),
        get_query_sec_upd(current_time),
        get_query_bidask_upd(current_time)
    ]
    if sequential:
        query = ";".join(sql_query_list)
        sql.get_table.exec_query(query)
    else:
        asyncio.run(sql.async_exec.exec_list(sql_query_list))


@sync_timed()
def process_signals(sequential=True):
    # после того как все новые котировки прогрузились
    sql_query_list = [
        get_query_signals_upd(),
        get_query_store_jump_events(),
        get_query_deact_by_endtime(),
    ]
    if sequential:
        query = ";".join(sql_query_list)
        sql.get_table.exec_query(query)
    else:
        asyncio.run(sql.async_exec.exec_list(sql_query_list))


@sync_timed()
def process_events(sequential=True):
    # после того как все новые котировки прогрузились
    sql_query_list = [
        get_query_events_update_news(),
        get_query_events_update_jumps(),
        get_query_events_update_prices()
    ]
    if sequential:
        query = ";".join(sql_query_list)
        sql.get_table.exec_query(query)
    else:
        asyncio.run(sql.async_exec.exec_list(sql_query_list))


def record_bucket(time, exec):
    bucket = int(time / exec)
    query = f"""insert into public.tgchannels_refresh_stat(bucket, num) VALUES({bucket} ,1)
    ON CONFLICT(bucket) DO UPDATE SET num = tgchannels_refresh_stat.num+1 
    """
    sql.get_table.exec_query(query)
    return bucket


start_refresh = compose_td_datetime("09:00:00")
end_refresh = compose_td_datetime("23:59:00")

if __name__ == '__main__':
    logger.info("starting refresh")
    if not tools.clean_processes.clean_proc("refresh", os.getpid(), 999999):
        print("something is already running")
        exit(0)

    moscow_tz = pytz.timezone('Europe/Moscow')

    while start_refresh <= datetime.datetime.now() < end_refresh:

        start = time.time()

        try:
            market_data_upd()
        except Exception as e:
            logger.error(e)
            process_error()
            # на всякий случай удалим задвоения в secquotes futquotes
            #sql_query_list = [get_remove_sec_duplicates, get_remove_fut_duplicates]
            #asyncio.run(sql.async_exec.exec_list(sql_query_list))

        try:
            process_signals()
            # смотрим на активацию евентов
            process_events()

            update_orders_state()
            #log_timing()
        except Exception as e:
            logger.error(e)
            process_error()

        bucket = record_bucket(time.time() - start, 0.25)
        if bucket >= 0:
            logger.warning(f"TOO LONG {datetime.datetime.now()} {time.time() - start}")

        #process_signal()
        time.sleep(0.25 - (time.time() % 0.25))
