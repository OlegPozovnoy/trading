import datetime
import os
from _decimal import Decimal
from datetime import timedelta

import pandas as pd
from tinkoff.invest import CandleInterval, Client
from tinkoff.invest.utils import quotation_to_decimal, now
from tinkoff.invest.services import InstrumentsService


from pandas import DataFrame

import sql.get_table
from Examples import Bars_upd_config
from dotenv import load_dotenv
import time
import sys
import signal


#import tools.pandas_full_view

load_dotenv(dotenv_path='./my.env')
engine = sql.get_table.engine

TOKEN = os.environ["INVEST_TOKEN"]

def candles_api_call(figi, start):
    with Client(TOKEN) as client:
        candles = client.get_all_candles(
            figi=figi,
            from_=start,
            to=now(),  # - timedelta(minutes=1),
            interval=CandleInterval.CANDLE_INTERVAL_1_MIN,
        )
        res = DataFrame(candles)
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

    tickers_df = DataFrame(tickers)
    tickers_df.to_csv("./Data/alltickers.csv", sep='\t')
    filter = tickers_df["exchange"].str.startswith('MOEX') | tickers_df["exchange"].str.startswith('FORTS')
    tickers_df = tickers_df[filter]
    tickers_df = tickers_df[tickers_df["ticker"].isin(ticker_list)]
    return tickers_df


def df_postprocessing(final):
    #print("postprocess before:", final.dtypes, final.head())
    for col in ['open', 'high', 'low', 'close']:
        final[col] = final[col].apply(lambda quotation: transform_candles(quotation))
        final[col] = final[col].astype('float')
    final.volume = pd.to_numeric(final.volume, downcast='integer')
    final['datetime'] = pd.to_datetime(final['time']).dt.tz_convert(tz="Europe/Moscow")
    final.drop(['time', 'is_complete'], axis=1, inplace=True)
    final.drop_duplicates(inplace=True)
    #print("postprocess after:", final.dtypes, final.head())
    return final


def transform_candles(quotation):
        try:
            if isinstance(quotation, float): return quotation
            return Decimal(quotation['units']) + quotation['nano'] / Decimal("10e8")
        except:
            print(f"conversion error: {quotation}")
            return Decimal(-1)


def update_import_params():
    tickers = Bars_upd_config.config["futures"]["secCodes"] + Bars_upd_config.config["equities"]["secCodes"]  # +
    df = get_ticker(tickers)
    engine.execute("delete from public.tinkoff_params")
    df.to_sql("tinkoff_params", engine, if_exists='replace')
    print(f"missing tickers: {set(tickers) - set(df['ticker'])}")
    return df

def import_new_tickers(refresh_tickers=False):
    df = update_import_params() if refresh_tickers else sql.get_table.query_to_df("select * from public.tinkoff_params")
    startTime = time.time()
    for idx, row in df.iterrows():
        try:
            print("loading", row['name'],  row['ticker'], row['figi'])
            query = f"select max(datetime) as dt from public.df_all_candles_t where security='{row['ticker']}'"
            last_row = sql.get_table.query_to_list(query)[0]['dt']

            start = now() - timedelta(days=90) if last_row is None else last_row+timedelta(minutes=1, seconds=1)

            print(f'last_row: {last_row}, start:{start}')
            candles = candles_api_call(row['figi'], start=start)
            candles['security'] = row['ticker']
            candles['class_code'] = row['class_code']

            if len(candles) > 0:
                print(f"{len(candles)} rows to append")
                candles = df_postprocessing(candles)
                candles.to_sql('df_all_candles_t', engine, if_exists='append', index=False)
        except Exception as e:
            print("import tickers error:" ,row, str(e))

    print(f'свечки залились за {(time.time() - startTime):.2f} с')


if __name__ == "__main__":
    startTime = time.time()
    time.sleep(1)
    signal.alarm(120)
    try:
        import_new_tickers(refresh_tickers=False)
    except:
        print("error", datetime.datetime.now())
        sys.exit(1)
    finally:
        print(datetime.datetime.now())







