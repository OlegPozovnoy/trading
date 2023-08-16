import datetime
import sql.get_table


def record_new_watch(doc, news_channel):
    codes = doc['important_tags']
    news_date = doc['date']
    tstamp = datetime.datetime.now()

    for code in codes:
        query_10mins = f"""SELECT code, board, min, max, mean, volume, count 
        FROM public.diffhistview_1510 
        where code = '{code}' 
        limit 1;"""
        params = sql.get_table.query_to_list(query_10mins)
        print(f"params: {params}")
        if len(params) == 1:
            params = params[0]
            query = f"""
            BEGIN;
            insert into public.order_discovery(code, date_discovery, news_time, channel_source, min_val, max_val, mean_val, volume) 
            values('{code}','{tstamp}','{news_date}','{news_channel}','{params['min']}','{params['max']}','{params['mean']}','{params['volume']}');
            COMMIT;
            """
            sql.get_table.exec_query(query)


def record_new_event(doc, news_channel, keyword):
    codes = doc['important_tags']
    news_date = doc['date']
    tstamp = datetime.datetime.now()

    for code in codes:
            query = f"""
            BEGIN;
            insert into public.event_news(code, date_discovery, news_time, channel_source) 
            values('{code}','{tstamp}','{news_date}','{news_channel}','{keyword}');
            COMMIT;
            """
            sql.get_table.exec_query(query)


