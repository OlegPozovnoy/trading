import datetime
import json
import random
from time import sleep
import os
import sys
import tools.clean_processes

class OrderProcesser():
    def __init__(self, func, timeout=0.5):
        self.tasks_list = []
        self.func = func
        self.timeout = timeout
    def add_task(self,task, timeout):
        self.tasks_list.append((task, datetime.datetime.now() + datetime.timedelta(seconds=timeout)))
        self.tasks_list = sorted(self.tasks_list, key=lambda x: x[1])
    def do_tasks(self):

        tasks_to_do = [task for task in self.tasks_list if task[1] < datetime.datetime.now()]
        for task in tasks_to_do:
            self.func(task[0])
        self.tasks_list = self.tasks_list[len(tasks_to_do):]

        return tasks_to_do


os.chdir(os.path.dirname(sys.argv[0]))
