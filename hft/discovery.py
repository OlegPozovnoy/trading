import datetime
import sql.get_table


def record_new_watch(codes, news_date, news_channel):
    tstamp = datetime.datetime.now()
    for code in codes:
        query = f"""insert into public.order_discovery(code, date_discovery, news_time, channel_source) values('{code}','{tstamp}','{news_date}','{news_channel}')"""
        sql.get_table.exec_query(query)

