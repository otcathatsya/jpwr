import os
import re

import pandas as pd


class power(object):
    def pow_to_float(self,pow):
        # Power is reported in the format xxx.xxW, so remove the last character.
        # We also handle the case when the power reports as N/A.
        try:
            return float(pow[:-1])
        except ValueError:
            return 0
    def init(self, power_value_dict : dict[str,list[float]]):
        import gcipuinfo
        self.ipu_info = gcipuinfo.gcipuinfo()
        device_count = len(self.ipu_info.getDevices())
        self.device_list = [idx for idx in range(device_count)]
        power_value_dict.update({
            f"gc:{idx}" : [] for idx in enumerate(self.device_list)
        })
    def measure(self, power_value_dict : dict[str,list[float]]):
        device_powers=self.ipu_info.getNamedAttributeForAll(gcipuinfo.IpuPower)
        device_powers = [self.pow_to_float(pow) for pow in device_powers if pow != "N/A"]
        for idx in self.device_list:
            power_value_dict[f"gc:{idx}"].append(device_powers[idx])
    def finalize(self, power_value_dict : dict[str,list[float]]):
        return {}
