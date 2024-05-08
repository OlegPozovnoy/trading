import datetime
import json
import logging
import os
import time
import sys
from _decimal import Decimal
from datetime import timedelta

import pandas as pd
from numba import njit
from tinkoff.invest import CandleInterval, Client
from tinkoff.invest.utils import quotation_to_decimal, now
from tinkoff.invest.services import InstrumentsService

import sql.get_table
from dotenv import load_dotenv

import tools.clean_processes
from tools.utils import async_timed, sync_timed

import asyncio

# import tools.pandas_full_view

load_dotenv(dotenv_path='./my.env')
engine = sql.get_table.engine

TOKEN = os.environ["INVEST_TOKEN"]
settings_path = os.environ['instrument_list_path']

logger = logging.getLogger()
logger.setLevel(logging.INFO)
@async_timed()
@njit()
async def candles_api_multi_call(df):
    result, res = [], pd.DataFrame()
    with Client(TOKEN) as client:
        for _, row in df.iterrows():
            print(f"importing {row['name']} {row['last_row']}")
            try:
                new_item = client.get_all_candles(
                    figi=row['figi'],
                    from_=row['last_row'],
                    to=now(),
                    interval=CandleInterval.CANDLE_INTERVAL_1_MIN,
                )
                res = pd.DataFrame(new_item)
                res['security'] = row['ticker']
                res['class_code'] = row['class_code']
                result.append(res)
            except Exception as e:
                print(str(e))
        res = pd.concat(result, axis=0) if len(result) > 0 else pd.DataFrame()
    print(f"{len(res)} rows imported ")
    return res


def get_ticker(ticker_list):
    """Example - How to get figi by name of ticker."""
    tickers = []
    with Client(TOKEN) as client:
        instruments: InstrumentsService = client.instruments
        for method in ["shares", "bonds", "futures"]:
            for item in getattr(instruments, method)().instruments:
                tickers.append(
                    {
                        "name": item.name,
                        "ticker": item.ticker,
                        "class_code": item.class_code,
                        "figi": item.figi,
                        "type": method,
                        "min_price_increment": quotation_to_decimal(
                            item.min_price_increment
                        ),
                        "currency": item.currency,
                        "exchange": item.exchange,
                    }
                )

    tickers_df = pd.DataFrame(tickers)
    exchange_filter = tickers_df["exchange"].str.startswith('MOEX') | tickers_df["exchange"].str.startswith('FORTS')
    tickers_df = tickers_df[exchange_filter]
    tickers_df = tickers_df[tickers_df["ticker"].isin(ticker_list)]
    return tickers_df


def df_postprocessing(final):
    for col in ['open', 'high', 'low', 'close']:
        final[col] = final[col].apply(lambda quotation: transform_candles(quotation))
        final[col] = final[col].astype('float')
    final.volume = pd.to_numeric(final.volume, downcast='integer')
    final['datetime'] = pd.to_datetime(final['time']).dt.tz_convert(tz="Europe/Moscow")
    final.drop(['time', 'is_complete'], axis=1, inplace=True)
    final.drop_duplicates(inplace=True)
    return final


def transform_candles(quotation):
    try:
        if isinstance(quotation, float):
            return quotation
        else:
            return Decimal(quotation['units']) + quotation['nano'] / Decimal("10e8")

    except Exception as ex:
        print(f"conversion error: {quotation}", str(ex))
        return Decimal(-1)


def update_import_params():
    with open(settings_path, "r") as fp:
        settings = json.load(fp)
    tickers = settings["futures"]["secCodes"] + settings["equities"]["secCodes"]
    if len(tickers) == 0:
        logger.error("list of tickers for import in file is empty")
        return
    df = get_ticker(tickers)

    sql.get_table.df_to_sql(df, "tinkoff_params")
    logger.info(f"missing tickers: {set(tickers) - set(df['ticker'])}")
    return df


@async_timed()
async def import_new_tickers(refresh_tickers=False):
    """
    Refresh df_all_candles_t table
    :param refresh_tickers: True if we take tickers from settings json, False if from tinkoff_params
    :return: None
    """
    df = update_import_params() if refresh_tickers else sql.get_table.query_to_df("select * from public.tinkoff_params")

    query = f"select security, max(datetime) as last_row from public.df_all_candles_t group by security"
    df_lastrec = sql.get_table.query_to_df(query)
    if len(df_lastrec) == 0:
        df_lastrec = pd.DataFrame(columns=['security', 'last_row'])
    df = df.merge(df_lastrec, left_on='ticker', right_on='security', how='left')
    df['last_row'] = (df['last_row'].apply
                      (lambda t: now() - timedelta(days=90) if pd.isnull(t) else t + timedelta(minutes=1, seconds=1)))

    candles = await candles_api_multi_call(df)
    if len(candles) > 0:
        print(f"{len(candles)} rows to append")
        candles = df_postprocessing(candles)
        candles.to_sql('df_all_candles_t', engine, if_exists='append', index=False)


@sync_timed()
def update_diffhist():
    query = "select * from public.diffhistview_t1510"
    df = sql.get_table.query_to_df(query)
    sql.get_table.df_to_sql(df, 'diffhist_t1510')

    query = "select * from public.diffhistview_5"  #тиньков не успевает
    df = sql.get_table.query_to_df(query)
    sql.get_table.df_to_sql(df, 'diffhist_t5')


if __name__ == "__main__":
    startTime = time.time()
    print(f"tinkoff candles: {datetime.datetime.now()} {os.getpid()}")
    if not tools.clean_processes.clean_proc("tinkoff_candles", os.getpid(), 3):
        print("something is already running")
        exit(0)
    time.sleep(1)
    try:
        asyncio.run(import_new_tickers(refresh_tickers=False))
    except Exception as ex:
        print("error", str(ex), datetime.datetime.now())
        sys.exit(1)
    finally:
        update_diffhist()
        print(datetime.datetime.now())
