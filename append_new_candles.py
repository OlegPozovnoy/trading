import Examples.Bars_upd
import time
import datetime
import os

if __name__ == '__main__':
    startTime = time.time()
    try:
        #Examples.Bars_upd.update_all_quotes()
        Examples.Bars_upd.update_all_quotes(to_remove=False, candles_num=10)
    finally:
        print(datetime.datetime.now())

