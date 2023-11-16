import asyncio
import json
import logging
import os
import sys
import time
import datetime
import pandas as pd
from dotenv import load_dotenv

import sql.get_table
import sql.async_exec
import subprocess

from nlp.mongo_tools import clean_mongo
from tinkoff_candles import import_new_tickers
from tools.utils import sync_timed, async_timed

load_dotenv(dotenv_path='./my.env')
engine = sql.get_table.engine
settings_path = os.environ['instrument_list_path']

logger = logging.getLogger()
logger.setLevel(logging.INFO)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


def calc_bollinger(end_cutoff=datetime.time(17, 45, 0)):
    df_ = sql.get_table.load_candles()
    df_['t'] = pd.to_datetime(df_['datetime'], format='%d.%m.%Y %H:%M')
    df_['dt'] = df_['t'].dt.date
    df_['time'] = df_['t'].dt.time

    # get last close
    df_bollinger = df_[df_['time'] <= end_cutoff] \
        .sort_values(['security', 'class_code', 'dt', 'time'], ascending=False) \
        .groupby(['security', 'class_code', 'dt']) \
        .head(1) \
        .reset_index()

    # get last 20 values
    df_bollinger = df_bollinger \
        .sort_values(['security', 'class_code', 'dt'], ascending=False) \
        .groupby(['security', 'class_code']) \
        .head(20) \
        .reset_index()

    # calc
    df_bollinger = df_bollinger \
        .groupby(['security', 'class_code']) \
        .agg(mean=('close', 'mean'), std=('close', 'std'), count=('close', 'count')) \
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

@async_timed()
async def clean_db():
    sql_query_list = [
        "DELETE	FROM public.secquoteshist where to_date(tradedate, 'DD.MM.YYYY') < (CURRENT_DATE-14);",
        "DELETE	FROM public.futquoteshist where to_date(tradedate, 'DD.MM.YYYY') < (CURRENT_DATE-14);",
        "DELETE FROM public.df_all_candles_t_arch WHERE datetime < now() - interval '90 days'",
        "DELETE FROM public.futquotesdiffhist 	where updated_at < (CURRENT_DATE-14);",
        "DELETE FROM public.secquotesdiffhist 	where updated_at < (CURRENT_DATE-14);",
        "DELETE	FROM public.secquotes where updated_at < (CURRENT_DATE-1);",
        "DELETE	FROM public.futquotes where updated_at < (CURRENT_DATE-1);",
        "DELETE FROM public.orders_in;",
        "DELETE FROM public.orders_out;",
        "DELETE FROM public.orders_in_tcs;",
        "DELETE FROM public.orders_out_tcs;",
        "DELETE	FROM public.pos_eq;",
        "DELETE	FROM public.pos_collat;",
        "DELETE	FROM public.deals;",
        "DELETE	FROM public.deorders;",
        "DELETE	FROM public.df_monitor;",
    ]
    await sql.async_exec.exec_list(sql_query_list)
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


def update_instrument_list(update_sec=True):
    setting = {'equities': {}, 'futures': {}}
    setting['equities']['classCode'] = "TQBR"
    setting['futures']['classCode'] = "SPBFUT"

    query_fut = "select distinct code from public.futquotes"
    query_sec = "select distinct code from public.secquotes"

    setting['futures']['secCodes'] = [x[0] for x in sql.get_table.exec_query(query_fut)]
    setting['equities']['secCodes'] = [x[0] for x in sql.get_table.exec_query(query_sec)] if update_sec else []

    if len(setting['futures']['secCodes']) + len(setting['equities']['secCodes']) == 0:
        logger.error("cant update instruments: fut&secquotes are empty")
        return

    settings_str = json.dumps(setting, indent=4)
    with open(settings_path, "w") as fp:
        fp.write(settings_str)
    print("instrument to import: ", settings_str)


if __name__ == '__main__':
    startTime = time.time()
    try:
        logger.info('Update import settings')
        #update_instrument_list()
        logger.info('Begin quotes reimport')
        #asyncio.run(import_new_tickers(True))
        logger.info('Bars updated')
        asyncio.run(clean_db())
        logger.info('DB Cleaned')
        calc_bollinger()
        logger.info('Bollinger recomputed')
        clean_mongo()
        logger.info("Mongodb duplicates removed")
        subprocess.run(["python", "morning_reports.py"])
    except Exception as e:
        logger.error(f"{e}")
    finally:
        print(datetime.datetime.now())
