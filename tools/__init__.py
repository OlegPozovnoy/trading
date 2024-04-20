import datetime


def compose_td_datetime(curr_time):
    now = datetime.datetime.now()
    my_datetime = datetime.datetime.strptime(curr_time, "%H:%M:%S").time()
    return now.replace(hour=my_datetime.hour, minute=my_datetime.minute, second=my_datetime.second, microsecond=0)
