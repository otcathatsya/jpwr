from jpwr.gpu.rocm import power
from jpwr.ctxmgr import get_power
import time

def main():
    time.sleep(10)
    

if __name__ == "__main__":
    with get_power([power()], 100) as measured_scope:
        print('Measuring Energy during main() call')
        try:
            main()
        except Exception as exc:
            import traceback
            print(f"Errors occured during training: {exc}")
            print(f"Traceback: {traceback.format_exc()}")
    print("Energy data:")
    print  (measured_scope.df)
    print("Energy-per-GPU-list:")
    energy_int,energy_cnt = measured_scope.energy()
    print(f"integrated: {energy_int}")
    print(f"from counter: {energy_cnt}")
