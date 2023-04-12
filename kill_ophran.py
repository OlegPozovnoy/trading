import os
from datetime import datetime


print(datetime.now())
#os.system("pkill -9 -f tinkoff_candles.sh")
os.system("pkill -9 -f update_levels.sh")
os.system("pkill -9 -f monitor.sh")