import unittest
import time
import pandas as pd

from jpwr.ctxmgr import get_power

class ignore_error_tester(unittest.TestCase):
    def test_ignore_succeed_fail(self):
        from .test_methods.always_fail import power as power_fail
        from .test_methods.always_succeed import power as power_succeed
        power_methods =  [power_succeed(), power_fail()]
        options = {
            "ignore_measure_errors" : True
        }
        with get_power(power_methods, 100, options) as measured_scope:
            try:
                time.sleep(1)
            except Exception as exc:
                import traceback
                print(f"Errors occured during power measurement of '{args.cmd}': {exc}")
                print(f"Traceback: {traceback.format_exc()}")
        power=measured_scope.df
        energy,additional = measured_scope.energy()

        self.assertTrue(power.empty)
        self.assertEqual(list(power.columns), 
                         ["timestamps",
                          "always_succeed:0",
                          "always_succeed:1",
                          "always_succeed:2",
                          "always_succeed:3", 
                          "always_fail:0",
                          "always_fail:1",
                          "always_fail:2",
                          "always_fail:3"])
        expect_energy = pd.Series([0.0 for i in range(8)],
            index=[
            "always_succeed:0",
            "always_succeed:1",
            "always_succeed:2",
            "always_succeed:3",
            "always_fail:0",
            "always_fail:1",
            "always_fail:2",
            "always_fail:3"
            ])
        self.assertTrue((expect_energy == energy).all())
        self.assertFalse(additional)

    def test_ignore_fail_succeed(self):
        from .test_methods.always_fail import power as power_fail
        from .test_methods.always_succeed import power as power_succeed
        power_methods =  [power_fail(),power_succeed()]
        options = {
            "ignore_measure_errors" : True
        }
        with get_power(power_methods, 100, options) as measured_scope:
            try:
                time.sleep(1)
            except Exception as exc:
                import traceback
                print(f"Errors occured during power measurement of '{args.cmd}': {exc}")
                print(f"Traceback: {traceback.format_exc()}")
        power=measured_scope.df
        energy,additional = measured_scope.energy()

        self.assertTrue(power.empty)
        self.assertEqual(list(power.columns), 
                         ["timestamps", 
                          "always_fail:0",
                          "always_fail:1",
                          "always_fail:2",
                          "always_fail:3",
                          "always_succeed:0",
                          "always_succeed:1",
                          "always_succeed:2",
                          "always_succeed:3"])
        expect_energy = pd.Series([0.0 for i in range(8)],
            index=[
            "always_fail:0",
            "always_fail:1",
            "always_fail:2",
            "always_fail:3",
            "always_succeed:0",
            "always_succeed:1",
            "always_succeed:2",
            "always_succeed:3"
            ])
        self.assertTrue((expect_energy == energy).all())
        self.assertFalse(additional)
