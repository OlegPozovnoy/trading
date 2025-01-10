import os
import psutil
import datetime
import signal


def clean_proc(keyword, pid, mins_threshold):
    """
    :param keyword: word mask of process
    :param pid: caller pid
    :param mins_threshold:minutes to wait before kill
    :return: True - can launch the program, False - something already running
    """
    cmd_list = [proc for proc in psutil.process_iter() if f'/home/{os.getlogin()}/PycharmProjects/trading/' in ' '.join(proc.cmdline())]
    cmd_list = [proc for proc in cmd_list if keyword in ' '.join(proc.cmdline())]
    print(f"\nprocesses filtered by keyword '{keyword}': \n{cmd_list} \nthreshold: {mins_threshold} mins")

    res = []

    if len(cmd_list) > 0:
        for proc in cmd_list:
            uptime = datetime.datetime.now() - datetime.datetime.fromtimestamp(proc.create_time())
            print(f'\npid: {proc.pid}',
                  f'\nscript name: {proc.name()}',
                  f'\nuptime: {(uptime.total_seconds() / 60):.2f}')

            res.append((proc.pid, proc.name(), uptime.total_seconds()/60))
    else:
        return True  # can be launched

    pid_process = list(filter(lambda x: pid == x[0], res))
    if len(pid_process) == 0:
        print(f"calling process {pid} is not found")
        raise ValueError
    print(f"\nall processes: {res}\ncaller_pid:{pid_process}")

    state = True
    killcount = 0
    print(f"\nLooking for processes to kill, our process in pid {pid_process[0][0]} uptime {pid_process[0][2]:.2f}")
    for item in res:
        print(f"checking {item}")
        if item[2] > mins_threshold:
            print(f"too long, killing {item}")
            os.kill(item[0], signal.SIGTERM)
            killcount += 1
        elif item[2] > (pid_process[0][2] + 1./60):
            print(f"process {item} is already running, shotting down")
            state = False

    if keyword == "create_tgchanne" and len(res) - killcount >=5:
        state = False
    print(f"{datetime.datetime.now()} returning: Is allowed to start = {state}")
    return state

