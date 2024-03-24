import asyncio
import logging
import sys
import time
import datetime

import sql.get_table
import sql.async_exec

from tools.utils import async_timed

engine = sql.get_table.engine

logger = logging.getLogger()
logger.setLevel(logging.INFO)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


@async_timed()
async def clean_db():
    sql_query_list = [
        "insert into deals_imp_arch select * from deals_imp on conflict (deal_id, tradedate) do nothing",
        "insert into deals_myhist select * from deals on conflict (deal_id, tradedate) do nothing"
    ]
    await sql.async_exec.exec_list(sql_query_list)


if __name__ == '__main__':
    startTime = time.time()
    try:
        asyncio.run(clean_db())
    except Exception as e:
        logger.error(f"{e}")
    finally:
        print(datetime.datetime.now())
