import asyncio
import os
from datetime import timedelta
import time

import pandas as pd
from tinkoff.invest import Client, AsyncClient, CandleInterval
from tinkoff.invest.utils import now

from dotenv import load_dotenv

import asyncio


load_dotenv(dotenv_path='./my.env')

TOKEN = os.environ["INVEST_TOKEN"]

async def get_candles():
    print('start')
    with AsyncClient(TOKEN) as client:
        tasks = [asyncio.create_task(client.get_all_candles(
            figi="BBG004730N88",
            from_=now() - timedelta(days=30),
            interval=CandleInterval.CANDLE_INTERVAL_HOUR,
        )),
            asyncio.create_task(client.get_all_candles(
                figi="BBG004730N88",
                from_=now() - timedelta(days=30),
                interval=CandleInterval.CANDLE_INTERVAL_HOUR,
            ))

        ]

        print(asyncio.gather(*tasks))
    return 0

async def main():
    #tasks = [get_candles(), get_candles()]
    #asyncio.gather(*tasks)
    await get_candles()

if __name__ == "__main__":
    startTime = time.time()
    asyncio.run(main())
    print(time.time() - startTime)