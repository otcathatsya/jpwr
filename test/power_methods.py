import unittest
from jpwr.ctxmgr import get_power
import time


class test_power_methods(unittest.TestCase):
    def dummy_workload():
        time.sleep(1)

    def _test_noerror(self, power_method):

        with get_power([power_method()], 100) as measured_scope:
            try:
                test_power_methods.dummy_workload()
            except Exception as exc:
                import traceback
                print(f"Errors occured during execution: {exc}")
                print(f"Traceback: {traceback.format_exc()}")
                raise exc

        power=measured_scope.df
        energy_int,additional = measured_scope.energy()

        # test succeeded if no exception raised

    def test_noerror_pynvml(self):
        try:
            from jpwr.gpu.pynvml import power
        except:
            self.skipTest("Failed importing pynvml method")

        self._test_noerror(power)

    def test_noerror_rocm(self):
        try:
            from jpwr.gpu.rocm import power
        except:
            self.skipTest("Failed importing rocm method")

    def test_noerror_gc(self):
        try:
            from jpwr.ipu.gc import power
        except:
            self.skipTest("Failed importing gc method")

        self._test_noerror(power)

    def test_noerror_gh(self):
        try:
            from jpwr.sys.gh import power
        except:
            self.skipTest("Failed importing gh method")

        self._test_noerror(power)
