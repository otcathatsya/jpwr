from pynvml import *

class power(object):
    def init(self, power_value_dict : dict[str,list[float]]):
        nvmlInit()
        device_count = nvmlDeviceGetCount()
        self.device_list = [nvmlDeviceGetHandleByIndex(idx) for idx in range(device_count)]
        power_value_dict.update({
            f"pynvml:{idx}" : [] for idx,handle in enumerate(self.device_list)
        })
    def measure(self, power_value_dict : dict[str,list[float]]):
        for idx,handle in enumerate(self.device_list):
            power = nvmlDeviceGetPowerUsage(handle)
            power_value_dict[f"pynvml:{idx}"].append(power*1e-3)
    def finalize(self, power_value_dict : dict[str,list[float]]):
        return {}

