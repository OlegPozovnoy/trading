import asyncio
import os
import traceback

import pytz

import sql.get_table
import sql.async_exec
import time
import datetime
import logging
import sys

import telegram
import tools.clean_processes
from refresh.orders_state import update_orders_state
from refresh.queries import get_query_fut_upd, get_query_sec_upd, get_query_signals_upd, get_query_store_jump_events, \
    get_query_deact_by_endtime, get_query_bidask_upd, get_query_events_update_news, get_query_events_update_jumps, \
    get_query_events_update_prices
from tools import compose_td_datetime

logger = logging.getLogger()
logger.setLevel(logging.INFO)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


def log_timing():
    query_fut = f"select max(updated_at), count(*), '{datetime.datetime.now()}' as cnt from public.futquotesdiff;"
    query_sec = f"select max(updated_at), count(*), '{datetime.datetime.now()}' as cnt from public.secquotesdiff;"

    last_sec = sql.get_table.query_to_list(query_sec)[0]
    last_fut = sql.get_table.query_to_list(query_fut)[0]
    logger.info(f"\nsec: {last_sec}\nfut: {last_fut}")




def process_error():
    error_msg = f"Error in quotes upd: {traceback.format_exc()}"
    telegram.send_message(error_msg, True)
    logger.error(error_msg)


start_refresh = compose_td_datetime("09:00:00")
end_refresh = compose_td_datetime("23:30:00")

if __name__ == '__main__':
    logger.info("starting refresh")
    if not tools.clean_processes.clean_proc("refresh", os.getpid(), 999999):
        print("something is already running")
        exit(0)

    moscow_tz = pytz.timezone('Europe/Moscow')

    while start_refresh <= datetime.datetime.now() < end_refresh:
        logger.info(datetime.datetime.now())

        try:
            current_time = datetime.datetime.now(moscow_tz).isoformat()

            sql_query_list = [
                get_query_fut_upd(current_time),
                get_query_sec_upd(current_time),
                get_query_bidask_upd()
            ]
            asyncio.run(sql.async_exec.exec_list(sql_query_list))
        except:
            process_error()
            # на всякий случай удалим задвоения в secquotes futquotes
            sql_query_list = ["delete from public.secquotes;", "delete from public.futquotes;"]
            asyncio.run(sql.async_exec.exec_list(sql_query_list))

        try:
            # после того как все новые котировки прогрузились
            sql_query_list = [
                get_query_signals_upd(),
                get_query_store_jump_events(),
                get_query_deact_by_endtime(),
            ]
            asyncio.run(sql.async_exec.exec_list(sql_query_list))

            # смотрим на активацию евентов
            sql_query_list = [
                get_query_events_update_news(),
                get_query_events_update_jumps(),
                get_query_events_update_prices()
            ]
            asyncio.run(sql.async_exec.exec_list(sql_query_list))

            update_orders_state()
            log_timing()
        except:
            process_error()

        # process_signal()
        time.sleep(0.5 - (time.time() % 0.5))
