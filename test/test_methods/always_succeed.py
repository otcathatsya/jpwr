class power(object):
    def init(self, power_value_dict : dict[str,list[float]]):
        power_value_dict.update({
            f"always_succeed:{idx}" : [] for idx in range(4)
        })
    def measure(self, power_value_dict : dict[str,list[float]]):
        for idx in range(4):
            power_value_dict[f"always_succeed:{idx}"].append(500)
    def finalize(self, power_value_dict : dict[str,list[float]]):
        return {}

