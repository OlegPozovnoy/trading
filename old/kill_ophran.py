import os
from datetime import datetime


print(datetime.now())
#os.system("pkill -9 -f tinkoff_candles.sh")
os.system("pkill -9 -f update_levels.sh")
os.system("pkill -9 -f monitor.sh")
os.system("pkill -9 -f create_tgchannels_db.py")
os.system("pkill -9 -f monitor.py")