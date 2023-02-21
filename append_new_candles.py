import Examples.Bars_upd
import time
import datetime
import sys
import signal


if __name__ == '__main__':
    startTime = time.time()
    signal.alarm(120)
    try:
        Examples.Bars_upd.update_all_quotes(to_remove=False, candles_num=10)
    except:
        print("error", datetime.datetime.now())
        sys.exit(1)
    finally:
        print(datetime.datetime.now())
