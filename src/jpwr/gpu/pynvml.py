import os
import subprocess
import io
import time

import pandas as pd
from pynvml import *
from multiprocessing import Process, Queue, Event

def power_loop(queue, event, interval):
    nvmlInit()
    device_count = nvmlDeviceGetCount()
    device_list = [nvmlDeviceGetHandleByIndex(idx) for idx in range(device_count)]
    power_value_dict = {
        idx : [] for idx in range(device_count)
    }
    power_value_dict['timestamps'] = []
    last_timestamp = time.time()

    while not event.is_set():
        for idx,handle in enumerate(device_list):
            power = nvmlDeviceGetPowerUsage(handle)
            power_value_dict[idx].append(power*1e-3)
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
        
        interval = 100 #ms
        self.smip = Process(target=power_loop,
                args=(self.power_queue, self.end_event, interval))
        self.smip.start()
        return self
    def __exit__(self, type, value, traceback):
        self.end_event.set()
        power_value_dict = self.power_queue.get()
        self.smip.join()

        self.df = pd.DataFrame(power_value_dict)
    def energy(self):
        import numpy as np
        _energy = []
        energy_df = self.df.loc[:,self.df.columns != 'timestamps'].astype(float).multiply(self.df["timestamps"].diff(),axis="index")/3600
        _energy = energy_df[1:].sum(axis=0).values.tolist()
        return _energy,[]
