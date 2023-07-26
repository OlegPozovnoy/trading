import time
import datetime
import pandas as pd

import sql.get_table

from nlp.mongo_tools import remove_news_duplicates
from tinkoff_candles import import_new_tickers

engine = sql.get_table.engine


def calc_bollinger(end_cutoff=datetime.time(17, 45, 0)):
    df_ = sql.get_table.load_candles()
    df_['t'] = pd.to_datetime(df_['datetime'], format='%d.%m.%Y %H:%M')
    df_['dt'] = df_['t'].dt.date
    df_['time'] = df_['t'].dt.time

    # get last close
    df_bollinger = df_[df_['time'] <= end_cutoff]\
        .sort_values(['security', 'class_code', 'dt', 'time'], ascending=False)\
        .groupby(['security', 'class_code', 'dt'])\
        .head(1)\
        .reset_index()

    # get last 20 values
    df_bollinger = df_bollinger\
        .sort_values(['security', 'class_code', 'dt'], ascending=False)\
        .groupby(['security', 'class_code'])\
        .head(20)\
        .reset_index()

    # calc
    df_bollinger = df_bollinger\
        .groupby(['security', 'class_code'])\
        .agg(mean=('close', 'mean'), std=('close', 'std'), count=('close', 'count'))\
        .reset_index()

    # custom cols
    df_bollinger['prct'] = df_bollinger['std'] / df_bollinger['mean']
    df_bollinger['up'] = df_bollinger['std'] * 2 + df_bollinger['mean']
    df_bollinger['down'] = -df_bollinger['std'] * 2 + df_bollinger['mean']

    # save
    sql.get_table.exec_query("delete from public.df_bollinger")
    df_bollinger.to_sql('df_bollinger', engine, if_exists='append')

    df_ = df_.sort_values(['security', 'class_code', 'dt', 'time'], ascending=True)
    df_['prev_close'] = df_.groupby('security')['close'].shift()
    df_['price_diff'] = df_['close'] - df_['prev_close']

    df_volumes = df_.groupby(['security', 'class_code', 'time']) \
        .agg(mean=('volume', 'mean'), std=('volume', 'std'), count=('volume', 'count'), close=('price_diff', 'std')) \
        .reset_index()

    df_volumes['prct'] = df_volumes['std'] / df_volumes['mean']
    df_volumes['up'] = df_volumes['std'] * 3 + df_volumes['mean']

    df_volumes['mean_avg'] = df_volumes.groupby('security')['mean'].transform(
        lambda x: x.rolling(10, 1, center=True).mean())
    df_volumes['std_avg'] = df_volumes.groupby('security')['std'].transform(
        lambda x: x.rolling(10, 1, center=True).mean())
    df_volumes['up_avga'] = df_volumes['std_avg'] * 3 + df_volumes['mean_avg']

    df_volumes['close_avg'] = df_volumes.groupby('security')['close'].transform(
        lambda x: x.rolling(10, 1, center=True).mean())

    sql.get_table.exec_query("delete from public.df_volumes")
    df_volumes.to_sql('df_volumes', engine, if_exists='append')


def clean_db():
    sql_query = """ 
    DELETE	FROM public.secquoteshist where to_date(tradedate, 'DD.MM.YYYY') < (CURRENT_DATE-14);
    DELETE	FROM public.secquotes;
    DELETE	FROM public.futquotes;
    DELETE  FROM public.orders_in;
    DELETE	FROM public.pos_eq;
    DELETE	FROM public.pos_collat;
    DELETE	FROM public.deals;
    DELETE	FROM public.deorders;
    DELETE	FROM public.df_monitor;
    DELETE	FROM public.futquoteshist where to_date(tradedate, 'DD.MM.YYYY') < (CURRENT_DATE-14);
    UPDATE public.orders_my set state=0, remains=0;
    DELETE  FROM public.futquotesdiffhist 	where updated_at < (CURRENT_DATE-14);
    DELETE  FROM public.secquotesdiffhist 	where updated_at < (CURRENT_DATE-14);  
    """
    engine.execute(sql_query)
    clean_tinkoff()


def clean_tinkoff():
    # 20 days for bollinger bands calculation
    query = "delete FROM public.df_all_candles_t_arch where datetime < (now() - interval '90 days')"
    engine.execute(query)
    query = """
        WITH moved_rows AS (
            DELETE FROM df_all_candles_t  a
            WHERE datetime < now() - interval '28 days'
            RETURNING a.* -- or specify columns
        )
        INSERT INTO df_all_candles_t_arch  --specify columns if necessary
        SELECT  * FROM moved_rows;    
    """
    engine.execute(query)
    query = "DELETE FROM df_all_candles_t_arch WHERE datetime < now() - interval '90 days'"
    engine.execute(query)


def update_instrument_list():
    query_fut = "select distinct code from public.futquotes"
    query_sec = "select distinct code from public.secquotes"

    fut_list = [x[0] for x in sql.get_table.exec_query(query_fut)]
    sec_list = [x[0] for x in sql.get_table.exec_query(query_sec)]

    setting = f"""config = {{
        "equities": {{
          "classCode" : "TQBR",
            "secCodes" : {sec_list}
        }},
        "futures":{{
            "classCode": "SPBFUT",
            "secCodes": {fut_list}
        }}
    }}
    """

    f = open("./Examples/Bars_upd_config.py", "w")
    f.write(setting)
    print(setting)


if __name__ == '__main__':
    startTime = time.time()
    try:
        print('Update import settings')
        update_instrument_list()
        print('Begin quotes reimport', datetime.datetime.now())
        import_new_tickers(True)
        print('Bars updated', datetime.datetime.now())
        clean_db()
        print('DB Cleaned', datetime.datetime.now())
        calc_bollinger()
        print('Bollinger recomputed', datetime.datetime.now())
        remove_news_duplicates()
        print("Mongodb duplicates removed")
    finally:
        print(datetime.datetime.now())
