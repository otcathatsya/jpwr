import os
import subprocess
import io
import time

import pandas as pd
try:
    from rsmiBindings import *
except:
    import sys
    rocm_path = os.getenv("ROCM_PATH")
    if rocm_path is None:
        rocm_path = "/opt/rocm/"
    sys.path.append(os.path.join(rocm_path, "libexec/rocm_smi/"))
    from rsmiBindings import *
from multiprocessing import Process, Queue, Event

def power_loop(queue, event, interval):
    rocmsmi = initRsmiBindings(silent=False)
    ret = rocmsmi.rsmi_init(0)
    if rsmi_status_t.RSMI_STATUS_SUCCESS != ret:
        raise RuntimeError("Failed initializing rocm_smi library")
    device_count = c_uint32(0)
    ret = rocmsmi.rsmi_num_monitor_devices(byref(device_count))
    if rsmi_status_t.RSMI_STATUS_SUCCESS != ret:
        raise RuntimeError("Failed enumerating ROCm devices")
    device_list = list(range(device_count.value))
    power_value_dict = {
        id : [] for id in device_list
    }
    power_value_dict['timestamps'] = []
    last_timestamp = time.time()
    start_energy_list = []
    for id in device_list:
        energy = c_uint64()
        energy_timestamp = c_uint64()
        energy_resolution = c_float()
        ret = rocmsmi.rsmi_dev_energy_count_get(id, 
                byref(energy),
                byref(energy_resolution),
                byref(energy_timestamp))
        if rsmi_status_t.RSMI_STATUS_SUCCESS != ret:
            raise RuntimeError(f"Failed getting Power of device {id}")
        start_energy_list.append(round(energy.value*energy_resolution.value,2)) # unit is uJ

    while not event.is_set():
        for id in device_list:
            power = c_uint32()
            ret = rocmsmi.rsmi_dev_power_ave_get(id, 0, byref(power))
            if rsmi_status_t.RSMI_STATUS_SUCCESS != ret:
                raise RuntimeError(f"Failed getting Power of device {id}")
            power_value_dict[id].append(power.value*1e-6) # value is uW
        timestamp = time.time()
        power_value_dict['timestamps'].append(timestamp)
        wait_for = max(0,1e-3*interval-(timestamp-last_timestamp))
        time.sleep(wait_for)
        last_timestamp = timestamp

    energy_list = [0.0 for _ in device_list]
    for id in device_list:
        energy = c_uint64()
        energy_timestamp = c_uint64()
        energy_resolution = c_float()
        ret = rocmsmi.rsmi_dev_energy_count_get(id, 
                byref(energy),
                byref(energy_resolution),
                byref(energy_timestamp))
        if rsmi_status_t.RSMI_STATUS_SUCCESS != ret:
            raise RuntimeError(f"Failed getting Power of device {id}")
        energy_list[id] = round(energy.value*energy_resolution.value,2) - start_energy_list[id]

    energy_list = [ (energy*1e-6)/3600 for energy in energy_list] # convert uJ to Wh
    queue.put(power_value_dict)
    queue.put(energy_list)
    rocmsmi.rsmi_shut_down()

class power(object):
    def init(self, power_value_dict : dict[str,list[float]]):
        self.rocmsmi = initRsmiBindings(silent=False)
        ret = self.rocmsmi.rsmi_init(0)
        if rsmi_status_t.RSMI_STATUS_SUCCESS != ret:
            raise RuntimeError("Failed initializing rocm_smi library")
        device_count = c_uint32(0)
        ret = self.rocmsmi.rsmi_num_monitor_devices(byref(device_count))
        if rsmi_status_t.RSMI_STATUS_SUCCESS != ret:
            raise RuntimeError("Failed enumerating ROCm devices")
        self.device_list = list(range(device_count.value))
        power_value_dict.update({
            f"rocm:{id}" : [] for id in self.device_list
        })
        self.start_energy_list = []
        for id in self.device_list:
            energy = c_uint64()
            energy_timestamp = c_uint64()
            energy_resolution = c_float()
            ret = self.rocmsmi.rsmi_dev_energy_count_get(id, 
                    byref(energy),
                    byref(energy_resolution),
                    byref(energy_timestamp))
            if rsmi_status_t.RSMI_STATUS_SUCCESS != ret:
                raise RuntimeError(f"Failed getting Power of device {id}")
            self.start_energy_list.append(round(energy.value*energy_resolution.value,2)) # unit is uJ
    def measure(self, power_value_dict : dict[str,list[float]]):
        for id in self.device_list:
            power = c_uint32()
            ret = self.rocmsmi.rsmi_dev_power_ave_get(id, 0, byref(power))
            if rsmi_status_t.RSMI_STATUS_SUCCESS != ret:
                raise RuntimeError(f"Failed getting Power of device {id}")
            power_value_dict[f"rocm:{id}"].append(float(power.value)*1e-6) # value is uW

    def finalize(self, power_value_dict : dict[str,list[float]]):
        energy_list = [0.0 for _ in self.device_list]
        for id in self.device_list:
            energy = c_uint64()
            energy_timestamp = c_uint64()
            energy_resolution = c_float()
            ret = self.rocmsmi.rsmi_dev_energy_count_get(id, 
                    byref(energy),
                    byref(energy_resolution),
                    byref(energy_timestamp))
            if rsmi_status_t.RSMI_STATUS_SUCCESS != ret:
                raise RuntimeError(f"Failed getting Power of device {id}")
            energy_list[id] = round(energy.value*energy_resolution.value,2) - self.start_energy_list[id]

        energy_list = [ (energy*1e-6)/3600 for energy in energy_list] # convert uJ to Wh
        self.rocmsmi.rsmi_shut_down()

        return {
            "energy_from_counter": pd.DataFrame({
                f"rocm:{idx}" : [value] for idx,value in zip(self.device_list,energy_list)
            })
        }

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
        self.energy_list_counter = self.power_queue.get()
        self.smip.join()

        self.df = pd.DataFrame(power_value_dict)
    def energy(self):
        import numpy as np
        _energy = []
        energy_df = self.df.loc[:,self.df.columns != 'timestamps'].astype(float).multiply(self.df["timestamps"].diff(),axis="index")/3600
        _energy = energy_df[1:].sum(axis=0).values.tolist()
        return _energy,self.energy_list_counter
