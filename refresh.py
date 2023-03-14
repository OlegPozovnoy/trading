import pandas as pd
import sql.get_table
import time
import datetime
import logging
import sys

query_upd = """BEGIN;
MERGE INTO public.futquotesdiff fqd
USING public.futquotes fq
ON fq.code = fqd.code
WHEN MATCHED THEN
UPDATE SET bid = fq.bid, ask = fq.ask, volume = fq.volume, openinterest = fq.openinterest, bidamount=fq.bidamount, askamount=fq.askamount, 
bid_inc = fq.bid - fqd.bid, ask_inc = fq.ask-fqd.ask, volume_inc = fq.volume-fqd.volume, updated_at=fq.updated_at, last_upd=NOW()  
WHEN NOT MATCHED THEN
INSERT (code, bid, bidamount, ask, askamount, volume, openinterest, bid_inc, ask_inc, volume_inc, updated_at, last_upd) 
VALUES (fq.code, fq.bid, fq.bidamount, fq.ask, fq.askamount, fq.volume, fq.openinterest, 0, 0, 0, fq.updated_at, NOW()); COMMIT;
"""

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger("refresh")


def update():
    sql.get_table.exec_query(query_upd)
    query = "select * from public.futquotesdiff;"
    s = pd.DataFrame(sql.get_table.exec_query(query))
    logger.info(s[:5].to_string())
    return s


def compose_td_datetime(curr_time):
    now = datetime.datetime.now()
    my_datetime = datetime.datetime.strptime(curr_time, "%H:%M:%S").time()
    return now.replace(hour=my_datetime.hour, minute=my_datetime.minute, second=my_datetime.second, microsecond=0)


start_refresh = compose_td_datetime("09:00:00")
end_refresh = compose_td_datetime("23:30:00")

if __name__ == '__main__':
    while start_refresh <= datetime.datetime.now() < end_refresh:
        logger.info(datetime.datetime.now())
        update()
        time.sleep(1.0 - (time.time() % 1.0))
