from jpwr.gpu.pynvml import GetPower as GetPowerPYNVML
from jpwr.gpu.rocm import GetPower as GetPowerROCM

import argparse
import subprocess
import traceback

gpu_methods = {
    "pynvml": GetPowerPYNVML,
    "rocm": GetPowerROCM
}

def parse_args():

    parser = argparse.ArgumentParser(description="jpwr - JSC power measurement tool")
    parser.add_argument("--gpu_method",
        type=str,
        required=True,
        choices=gpu_methods.keys(),
        help=f"Choose method by which to measure GPU power Available: [{','.join(gpu_methods.keys())}]")
    parser.add_argument(
        "cmd",
        nargs=argparse.REMAINDER,
        help="Command to run with the tool",
    )

    return parser.parse_args()


def main():

    args = parse_args()
    if args.cmd is None:
        print("no command specified")
        exit(-1)

    GetPower = gpu_methods[args.gpu_method]

    print(f"Measuring Energy while executing {args.cmd}")
    with GetPower() as measured_scope:
        try:
            result = subprocess.run(args.cmd, text=True)
            print(result.stdout)
            print(result.stderr)
        except Exception as exc:
            import traceback
            print(f"Errors occured during power measurement of '{args.cmd}': {exc}")
            print(f"Traceback: {traceback.format_exc()}")
    print("Energy data:")
    print  (measured_scope.df)
    print("Energy-per-GPU-list:")
    energy_int,energy_cnt = measured_scope.energy()
    print(f"integrated: {energy_int}")
    print(f"from counter: {energy_cnt}")
