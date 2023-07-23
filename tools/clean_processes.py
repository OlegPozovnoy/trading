import os
import psutil
import datetime
import signal


def clean_proc(keyword, pid, mins_threshold):
    cmd_list = [proc for proc in psutil.process_iter() if f'/home/{os.getlogin()}/PycharmProjects/trading/' in ' '.join(proc.cmdline())]
    cmd_list = [proc for proc in cmd_list if keyword in ' '.join(proc.cmdline())]
    print(f"filter by {keyword} step2 {cmd_list}")

    res = []

    if len(cmd_list) > 0:
        for proc in cmd_list:
            uptime = datetime.datetime.now() - datetime.datetime.fromtimestamp(proc.create_time())
            print(f'\n{proc.pid}: Script name: {proc.name()}',
                  f'\ncmdline: {cmd_list}',
                  f'\nuptime: {uptime.total_seconds() / 60}',
                  f'\nthreshold: {mins_threshold}')

            res.append((proc.pid, proc.name(), uptime.total_seconds()/60))
    else:
        return True  # can be launched

    pid_process = list(filter(lambda x: pid == x[0], res))
    if len(pid_process) == 0:
        print(f"calling process {pid} is not found")
        raise ValueError
    print(f"res: {res}\n pid_process(caller):{pid_process}")

    state = True
    killcount = 0
    for item in res:
        print(f"False: {item[2]} {pid_process[0][2] + 1. / 60}")
        if item[2] > mins_threshold:
            print(f"Killing {item}")
            os.kill(item[0], signal.SIGTERM)
            killcount += 1
        elif item[2] > (pid_process[0][2] + 1./60):
            state = False  # something is running

    if keyword == "create_tgchanne" and len(res) - killcount >=5:
        state = False
    print(f"state: {state}")
    return state

