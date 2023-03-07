from sqlalchemy import create_engine
import sql.get_table

import Examples.Bars_upd
import time
import datetime
import os

import pandas as pd
from sqlalchemy import create_engine


def calc_bollinger(end_cutoff=datetime.time(17, 45, 0)):
    engine = create_engine('postgresql://postgres:postgres@localhost:5432/test')
    df_ = pd.read_csv('./Data/candles.csv', sep='\t')
    df_['t'] = pd.to_datetime(df_['datetime'], format='%d.%m.%Y %H:%M')
    df_['dt'] = df_['t'].dt.date
    df_['time'] = df_['t'].dt.time

    # get last close
    df_bollinger = df_[df_['time'] <= end_cutoff].sort_values(['security', 'class_code', 'dt', 'time'], ascending=False)\
        .groupby(['security', 'class_code', 'dt']).head(1).reset_index()

    # get last 20 values
    df_bollinger = df_bollinger.sort_values(['security', 'class_code', 'dt'], ascending=False)\
        .groupby(['security', 'class_code']).head(20).reset_index()

    # calc
    df_bollinger = df_bollinger.groupby(['security', 'class_code'])\
        .agg(mean=('close', 'mean'), std=('close', 'std'), count=('close', 'count')).reset_index()

    # custom cols
    df_bollinger['prct'] = df_bollinger['std'] / df_bollinger['mean']
    df_bollinger['up'] = df_bollinger['std'] * 2 + df_bollinger['mean']
    df_bollinger['down'] = -df_bollinger['std'] * 2 + df_bollinger['mean']
    # save
    df_bollinger.to_csv('./Data/bollinger.csv', sep='\t')

    sql.get_table.exec_query("delete from public.df_bollinger")
    df_bollinger.to_sql('df_bollinger', engine, if_exists='append')
    #print(df_bollinger[df_bollinger['class_code'] == 'SPBFUT'])

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

    df_volumes.to_csv('./Data/volumes.csv', sep='\t')

    sql.get_table.exec_query("delete from public.df_volumes")
    df_volumes.to_sql('df_volumes', engine, if_exists='append')
    #print(df_volumes.head(5))


def clean_db():
    engine = create_engine('postgresql://postgres:postgres@localhost:5432/test')
    sql_query = """ DELETE	FROM public.secquoteshist where to_date(tradedate, 'DD.MM.YYYY') < (CURRENT_DATE-14);
    DELETE	FROM public.futquoteshist where to_date(tradedate, 'DD.MM.YYYY') < (CURRENT_DATE-14);
    DELETE	FROM public.bigdealshist where to_date(tradedate, 'DD.MM.YYYY') < (CURRENT_DATE-14);"""
    engine.execute(sql_query)


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
        Examples.Bars_upd.update_all_quotes(candles_num=20000)
        print('Bars updated', datetime.datetime.now())
        clean_db()
        print('DB Cleaned', datetime.datetime.now())
        calc_bollinger()
        print('Bollinger recomputed', datetime.datetime.now())
    finally:
        print(datetime.datetime.now())
