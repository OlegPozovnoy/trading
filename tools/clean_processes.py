import os, psutil, datetime
import random
import signal
from time import sleep


def clean_proc(keyword, pid, mins_threshold):
    cmd_list = [proc for proc in psutil.process_iter() if f'/home/{os.getlogin()}/PycharmProjects/trading/' in ' '.join(proc.cmdline())]
    #for proc in cmd_list: print("1:", proc.cmdline())
    #cmd_list = [proc for proc in cmd_list if f'/home/{os.getlogin()}/PycharmProjects/trading/venv/bin/python' not in ' '.join(proc.cmdline())]
    #for proc in cmd_list: print("2:", proc.cmdline())
    cmd_list = [proc for proc in cmd_list if keyword in ' '.join(proc.cmdline())]
    #for proc in cmd_list: print("3:", proc.cmdline())

    res = []

    if len(cmd_list) > 0:
        for proc in cmd_list:
            uptime = datetime.datetime.now() - datetime.datetime.fromtimestamp(proc.create_time())
            print(f'{proc.pid}: Script name: {proc.name()}, cmdline: {cmd_list} uptime: {uptime.total_seconds() / 60} threshold: {mins_threshold}')
            res.append((proc.pid, proc.name(), cmd_list, uptime.total_seconds()/60))
    else:
        return True  # can be launched

    pid_process = list(filter(lambda x: pid == x[0], res))
    if len(pid_process) == 0:
        print(f"calling process {pid} is not found")
        raise ValueError

    state = True
    for item in res:
        if item[3] > mins_threshold:
            print(f"Killing {item}")
            os.kill(item[0], signal.SIGTERM)
            #os.system(f"pkill -9 -f {item[0]}") # too long
        elif item[3] > (pid_process[0][3] + 1./60):
            state = False  # something is running
    return state



sleep(random.random())
cmd_list = [proc for proc in psutil.process_iter() if f'/home/{os.getlogin()}/PycharmProjects/trading/' in ' '.join(proc.cmdline())]
if len([proc for proc in cmd_list if "refresh" in ' '.join(proc.cmdline())]) == 0:
    print("launching refresh...")
    os.system(f'/home/{os.getlogin()}/PycharmProjects/trading/bash/refresh.sh')
