import os, psutil, datetime
import random
import signal
from time import sleep


def clean_proc(keyword, pid, mins_threshold):
    cmd_list = [proc for proc in psutil.process_iter() if f'/home/{os.getlogin()}/PycharmProjects/trading/' in ' '.join(proc.cmdline())]
    cmd_list = [proc for proc in cmd_list if keyword in ' '.join(proc.cmdline())]
    print(f"filter by {keyword} step2 {cmd_list}")

    res = []

    if len(cmd_list) > 0:
        for proc in cmd_list:
            uptime = datetime.datetime.now() - datetime.datetime.fromtimestamp(proc.create_time())
            print(f'{proc.pid}: Script name: {proc.name()}, cmdline: {cmd_list} uptime: {uptime.total_seconds() / 60} threshold: {mins_threshold}')
            res.append((proc.pid, proc.name(), uptime.total_seconds()/60))
    else:
        return True  # can be launched

    pid_process = list(filter(lambda x: pid == x[0], res))
    if len(pid_process) == 0:
        print(f"calling process {pid} is not found")
        raise ValueError
    print(f"res: {res}\n pid_process(caller):{pid_process}")

    state = True
    for item in res:
        print(f"False: {item[2]} {pid_process[0][2] + 1. / 60}")
        if item[2] > mins_threshold:
            print(f"Killing {item}")
            os.kill(item[0], signal.SIGTERM)
            #os.system(f"pkill -9 -f {item[0]}") # too long
        elif item[2] > (pid_process[0][2] + 1./60):
            state = False  # something is running
    print(f"state: {state}")
    return state



#sleep(random.random())
#cmd_list = [proc for proc in psutil.process_iter() if f'/home/{os.getlogin()}/PycharmProjects/trading/' in ' '.join(proc.cmdline())]
#if len([proc for proc in cmd_list if "refresh" in ' '.join(proc.cmdline())]) == 0:
#    print("launching refresh...")
#    os.system(f'/home/{os.getlogin()}/PycharmProjects/trading/bash/refresh.sh')
