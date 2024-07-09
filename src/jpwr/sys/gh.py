import os
import io
import time

import pandas as pd
from pynvml import *
from multiprocessing import Process, Queue, Event

def power_loop(queue, event, interval):
    power_value_dict = {
        'Module' : [],
        'Grace' : [],
        'CPU' : [],
        'SysIO' : [],
        'timestamps' : [],
    }
    last_timestamp = time.time()

    while not event.is_set():
        with open("/sys/class/hwmon/hwmon1/device/power1_average") as f:
            power_value_dict["Module"].append(1e-6*float(f.read()))
        with open("/sys/class/hwmon/hwmon2/device/power1_average") as f:
            power_value_dict["Grace"].append(1e-6*float(f.read()))
        with open("/sys/class/hwmon/hwmon3/device/power1_average") as f:
            power_value_dict["CPU"].append(1e-6*float(f.read()))
        with open("/sys/class/hwmon/hwmon4/device/power1_average") as f:
            power_value_dict["SysIO"].append(1e-6*float(f.read()))

        timestamp = time.time()
        power_value_dict['timestamps'].append(timestamp)
        wait_for = max(0,1e-3*interval-(timestamp-last_timestamp))
        time.sleep(wait_for)
        last_timestamp = timestamp
    queue.put(power_value_dict)

class GetPower(object):
    def __enter__(self):
        self.end_event = Event()
        self.power_queue = Queue()
        
        interval = 1000 #ms
        self.pwp = Process(target=power_loop,
                args=(self.power_queue, self.end_event, interval))
        self.pwp.start()
        return self
    def __exit__(self, type, value, traceback):
        self.end_event.set()
        power_value_dict = self.power_queue.get()
        self.pwp.join()

        self.df = pd.DataFrame(power_value_dict)
    def energy(self):
        import numpy as np
        _energy = []
        energy_df = self.df.loc[:,self.df.columns != 'timestamps'].astype(float).multiply(self.df["timestamps"].diff(),axis="index")/3600
        _energy = energy_df[1:].sum(axis=0).values.tolist()
        return _energy,[]
