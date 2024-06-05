import datetime

import telegram_send
import asyncio
import sql.get_table
from datetime import datetime, timedelta
from tools.utils import sync_timed

def store_plita_values():
    query = """
    insert into 
     public.report_plita_tbl
    WITH orderbook_data AS (
        SELECT 
            code,
            date_trunc('minute', datetime) AS rounded_timestamp,
            MAX(CASE WHEN abnormal = true AND ba = 'bid' THEN price ELSE NULL END) AS bid,
            MAX(CASE WHEN abnormal = true AND ba = 'bid' THEN quantity ELSE NULL END) AS q_bid,
            MIN(CASE WHEN abnormal = true AND ba = 'ask' THEN price ELSE NULL END) AS ask,
            MAX(CASE WHEN abnormal = true AND ba = 'ask' THEN quantity ELSE NULL END) AS q_ask
        FROM df_all_orderbook_arch
        WHERE abnormal = true AND ba IN ('bid', 'ask')
        GROUP BY code, date_trunc('minute', datetime)
    )
    SELECT 
        t_main.security, 
        t_main.datetime, 
        orderbook_data.bid::double precision, 
        t_main.close,
        orderbook_data.q_bid, 
        orderbook_data.ask::double precision, 
        orderbook_data.q_ask
    FROM 
        public.df_all_candles_t t_main
    LEFT JOIN orderbook_data
        ON t_main.security = orderbook_data.code 
        AND t_main.datetime = orderbook_data.rounded_timestamp
    WHERE 
        (orderbook_data.bid IS NOT NULL 
        OR orderbook_data.ask IS NOT NULL)
        and t_main.datetime > NOW() - INTERVAL '10 minutes'
        on conflict (security, datetime) do nothing
    """
    sql.get_table.exec_query(query)
