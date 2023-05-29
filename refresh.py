import os

import pandas as pd
import sql.get_table
import time
import datetime
import logging
import sys

import tools.clean_processes

engine = sql.get_table.engine

query_fut_upd = """
MERGE INTO public.futquotesdiff fqd
USING public.futquotes fq
ON fq.code = fqd.code
WHEN MATCHED THEN
UPDATE SET bid = fq.bid, ask = fq.ask, volume = fq.volume, openinterest = fq.openinterest, bidamount=fq.bidamount, askamount=fq.askamount, 
bid_inc = fq.bid - fqd.bid, ask_inc = fq.ask-fqd.ask, volume_inc = fq.volume-fqd.volume, updated_at=fq.updated_at, last_upd=NOW()  
WHEN NOT MATCHED THEN
INSERT (code, bid, bidamount, ask, askamount, volume, openinterest, bid_inc, ask_inc, volume_inc, updated_at, last_upd) 
VALUES (fq.code, fq.bid, fq.bidamount, fq.ask, fq.askamount, fq.volume, fq.openinterest, 0, 0, 0, fq.updated_at, NOW()); 
"""


query_sec_upd="""
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
last_upd=NOW()  
WHEN NOT MATCHED THEN
INSERT (code, bid, bidamount, ask, askamount, volume, bid_inc, ask_inc, volume_inc, updated_at, last_upd) 
VALUES (fq.code, fq.bid, fq.bidamount, fq.ask, fq.askamount, fq.volume, 0, 0, 0, fq.updated_at, NOW());
"""


query_sig_upd = """
insert into public.signal_arch(tstz, code, date_discovery, channel_source, news_time, min_val, max_val, mean_val, volume, board, min, max, last_volume, count)
select * from public.signal;
"""


logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger("refresh")


def update():
    sql.get_table.exec_query(query_fut_upd)
    sql.get_table.exec_query(query_sec_upd)
    #store_jumps()
    query = "select * from public.futquotesdiff;"
    s = pd.DataFrame(sql.get_table.exec_query(query))
    logger.info(f"df length: {len(s)}")
    return s


def compose_td_datetime(curr_time):
    now = datetime.datetime.now()
    my_datetime = datetime.datetime.strptime(curr_time, "%H:%M:%S").time()
    return now.replace(hour=my_datetime.hour, minute=my_datetime.minute, second=my_datetime.second, microsecond=0)



def store_jumps():
    query = "select * from public.jumps;"
    df_jumps = pd.DataFrame(sql.get_table.exec_query(query))
    if len(df_jumps)>0:
        df_jumps.to_sql('df_jumps', engine, if_exists='append')


start_refresh = compose_td_datetime("09:00:00")
end_refresh = compose_td_datetime("23:30:00")

if __name__ == '__main__':
    print("starting refresh")
    print(datetime.datetime.now())
    if not tools.clean_processes.clean_proc("refresh", os.getpid(), 999999):
        print("something is already running")
        exit(0)

    while start_refresh <= datetime.datetime.now() < end_refresh:
        logger.info(datetime.datetime.now())
        try:
            update()
            sql.get_table.exec_query(query_sig_upd)
        except Exception as e:
            print(e)

        time.sleep(0.5 - (time.time() % 0.5))
