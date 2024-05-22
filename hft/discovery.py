import datetime
import re

import sql.get_table
from tools.utils import sync_timed


#@sync_timed()
def record_new_watch(doc, news_channel):
    """
    insert event to public.order_discovery
    :param doc:
    :param news_channel:
    :return:
    """
    codes = doc['important_tags']
    news_date = doc['date']
    tstamp = datetime.datetime.now()

    for code in codes:
        query_10mins = f"""SELECT code, board, min, max, mean, volume, count 
        FROM public.diffhist_t1510 
        where code = '{code}' 
        limit 1;"""
        params = sql.get_table.query_to_list(query_10mins)
        print(f"params: {params}")
        if len(params) == 1:
            params = params[0]
            query = f"""
            insert into public.order_discovery(code, date_discovery, news_time, channel_source, min_val, max_val, mean_val, volume) 
            values('{code}','{tstamp}','{news_date}','{news_channel}','{params['min']}','{params['max']}','{params['mean']}','{params['volume']}');
            """
            sql.get_table.exec_query(query)


#@sync_timed()
def record_new_event(doc, news_channel, keyword, msg):
    """
    insert msg to public.event_news
    :param doc:
    :param news_channel:
    :param keyword:
    :param msg:
    :return:
    """
    codes = doc['important_tags']
    news_date = doc['date']
    tstamp = datetime.datetime.now()

    for code in codes:
        query = f"""
            insert into public.event_news(code, date_discovery, news_time, channel_source, keyword, msg) 
            values('{code}','{tstamp}','{news_date}','{news_channel}','{keyword}','{msg}')
            on conflict(code, news_time, channel_source) do nothing;
            """
        sql.get_table.exec_query(query)

@sync_timed()
def fast_dividend_process(row, fulltext):
    codes = row['important_tags']

    index = fulltext.find('на одну')
    if index < 0: return

    is_execute = (datetime.datetime.now().hour >= 10)

    fulltext = fulltext[max(index - 50, 0):index + 1]

    for code in codes:
        # прив не смотрим
        if len(code) == 4:
            # это первая новость за посл час
            query = f"""SELECT 1
            FROM public.event_news where 
            code = '{code}' 
            and keyword = 'дивиденд'
            and news_time > NOW() - interval '1 hour'
            """
            if len(sql.get_table.query_to_list(query)) == 0:
                if datetime.datetime.now() - row['date'] < datetime.timedelta(0, 5):
                    pattern = r"(\d+[,.]?\d*)\s*руб"  # r"(\d+)\s+рубл"
                    myreg = re.search(pattern, fulltext)
                    if myreg and len(myreg.groups()) >= 1:
                        dividend = myreg.group(1)
                    else:
                        dividend = None

                    dividend = dividend.replace(',', '.')

                    if dividend is not None:
                        dividend = float(dividend)
                        query = f"""
                        SELECT * FROM public.order_dividend
	                    where ticker = '{code}'
                        and is_activated = false
                        limit 1;
                        """

                        orders = sql.get_table.query_to_list(query)
                        if len(orders) == 1:
                            if dividend <= orders[0]['divval_lte'] and is_execute:
                                query = f"""
                                update public.orders_my
                                set state = 1
                                where id = {orders[0]['lte_order_id']};
                                """
                                sql.get_table.exec_query(query)
                            if orders[0]['divval_gte'] <= dividend <= 2.5 * orders[0]['divval_gte'] and is_execute:
                                query = f"""
                                update public.orders_my
                                set state = 1
                                where id = {orders[0]['gte_order_id']};
                                """
                                sql.get_table.exec_query(query)

                            query = f"""
                            update public.order_dividend
                            set is_activated = true,
                            activation_time = NOW(),
                            dividend = {str(dividend)}
                            """
                            sql.get_table.exec_query(query)
