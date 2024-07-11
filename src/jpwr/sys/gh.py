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


class power(object):
    hwmon_base = "/sys/class/hwmon/"
    def init(self, power_value_dict : dict[str,list[float]]):
        # sort by hwmon number
        self.hwmons = sorted(os.listdir(self.hwmon_base),key=lambda x: int(x[5:]))
        for hwmon in self.hwmons:
            hwmon_path = os.path.join(self.hwmon_base, hwmon)
            oem_path = os.path.join(hwmon_path, "device/power1_oem_info")
            if not os.path.exists(oem_path):
                continue
            with open(oem_path, 'r') as oem_fd:
                name = oem_fd.read()
                name = name.strip()

            power_value_dict[f"gh:{name}"] = []
    def measure(self, power_value_dict : dict[str,list[float]]):
        for hwmon in self.hwmons:
            hwmon_path = os.path.join(self.hwmon_base, hwmon)
            oem_path = os.path.join(hwmon_path, "device/power1_oem_info")
            if not os.path.exists(oem_path):
                continue
            with open(oem_path, 'r') as oem_fd:
                name = oem_fd.read()
                name = name.strip()
            power_path = os.path.join(hwmon_path, "device/power1_average")
            with open(power_path) as power_fd:
                value = 1e-6*float(power_fd.read())

            power_value_dict[f"gh:{name}"].append(value)

    def finalize(self, power_value_dict : dict[str,list[float]]):
        return {}

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
