import datetime
import os
import subprocess


def compose_td_datetime(curr_time):
    now = datetime.datetime.now()
    my_datetime = datetime.datetime.strptime(curr_time, "%H:%M:%S").time()
    return now.replace(hour=my_datetime.hour, minute=my_datetime.minute, second=my_datetime.second, microsecond=0)


def get_pc_code():
    mac = subprocess.check_output(["ifconfig | grep ether | head -n 1 | awk '{print $2}'"], shell=True)
    if mac == b'02:42:34:16:e9:56\n':
        return "laptop"
    elif mac == b'02:42:a7:f0:60:45\n':
        return "moscow"
    else:
        return "unknown"

def get_wg_interface():
    try:
        wg = subprocess.check_output(["wg show"], shell=True, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        wg = e.output
    finally:
        if 'llaptop' in str(wg):
            return "llaptop"
        elif 'moscow' in str(wg):
            return "moscow"
        else:
            return "unknown"

def get_pc_info():
    return get_pc_code(), get_wg_interface()


print(get_pc_info()==('laptop', 'llaptop'))