import os
from _decimal import Decimal
from datetime import timedelta

import pandas as pd
from tinkoff.invest import CandleInterval, Client
from tinkoff.invest.utils import now
from tinkoff.invest.utils import quotation_to_decimal

from pandas import DataFrame

from tinkoff.invest import Client, SecurityTradingStatus
from tinkoff.invest.services import InstrumentsService

import sql.get_table
from Examples import Bars_upd_config
from dotenv import load_dotenv
import time

load_dotenv(dotenv_path='./my.env')
engine = sql.get_table.engine


def main(figi, minutes=10):
    with Client(TOKEN) as client:
        start = now() - timedelta(days=14)
        print(start, type(start))
        candles = client.get_all_candles(
            figi=figi,
            from_=start,
            to=now(),  # - timedelta(minutes=1),
            interval=CandleInterval.CANDLE_INTERVAL_1_MIN,
        )
        return DataFrame(candles)


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
    print(tickers_df)
    return tickers_df


if __name__ == "__main__":
    TOKEN = os.environ["INVEST_TOKEN"]
    tickers = Bars_upd_config.config["futures"]["secCodes"]  + Bars_upd_config.config["equities"]["secCodes"] #+
    df = get_ticker(tickers)
    engine.execute("delete from public.tinkoff_params")
    df.to_sql("tinkoff_params", engine, if_exists='replace')
    print(f"missing tickers: {set(tickers) - set(df['ticker'])}")

    final = pd.DataFrame()
    #open, close high low: float64 volume int16 security classcode datetime:pdtodatetime

    startTime = time.time()
    for idx, row in df.iterrows():
        print(row['name'], row['figi'])
        candles = main(row['figi'], 600)
        candles['security'] = row['ticker']
        candles['class_code'] = row['class_code']
        final = pd.concat([final, candles])

    #final = final[final['is_complete'] == True]
    print(final.columns)

    for col in ['open', 'high', 'low', 'close']:
        final[col] = final[col].apply(
            lambda quotation: Decimal(quotation['units']) + quotation['nano'] / Decimal("10e8"))
        final[col] = final[col].astype('float')
    final.volume = pd.to_numeric(final.volume, downcast='integer')
    final['datetime'] = pd.to_datetime(final['time']).dt.tz_convert(tz="Europe/Moscow")
    final['datetime'] = pd.to_datetime(final['time']).dt.tz_localize(None)
    final.drop(['time', 'is_complete'], axis=1, inplace=True)

    final.to_sql('df_all_candles_t', engine, if_exists='replace', index=False)
    print(final.dtypes)
    print(f'свечки залились за {(time.time() - startTime):.2f} с')
