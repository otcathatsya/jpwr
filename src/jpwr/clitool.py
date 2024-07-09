import argparse
import subprocess
import traceback

def get_pynvml_method():
    from jpwr.gpu.pynvml import GetPower as GetPowerPYNVML
    return GetPowerPYNVML

def get_rocm_method():
    from jpwr.gpu.rocm import GetPower as GetPowerROCM
    return GetPowerROCM

def get_gh_method():
    from jpwr.sys.gh import GetPower as GetPowerGH
    return GetPowerGH


gpu_methods = {
    "pynvml": get_pynvml_method,
    "rocm": get_rocm_method
}

sys_methods = {
    "gh": get_gh_method,
}

def parse_args():

    parser = argparse.ArgumentParser(description="jpwr - JSC power measurement tool")
    parser.add_argument("--gpu_method",
        type=str,
        required=True,
        choices=gpu_methods.keys(),
        help=f"Choose method by which to measure GPU power Available: [{','.join(gpu_methods.keys())}]")
    parser.add_argument("--sys_method",
        type=str,
        choices=sys_methods.keys(),
        help=f"Choose method by which to measure System power: [{','.join(sys_methods.keys())}]")
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

    GetPower = gpu_methods[args.gpu_method]()

    # TODO: some sort of plugin design instead of this nonsense
    if not args.sys_method:
        print(f"Measuring Energy while executing {args.cmd}")
        with GetPower() as measured_scope:
            try:
                result = subprocess.run(args.cmd, text=True)
                if result.stdout is not None:
                    print(result.stdout)
                if result.stderr is not None:
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
    else:
        GetPowerSys = sys_methods[args.sys_method]()
        print(f"Measuring Energy while executing {args.cmd}")
        with GetPower() as measured_scope,GetPowerSys() as measured_scope_sys:
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
        print("Energy data:")
        print  (measured_scope_sys.df)
        print("Energy-per-GPU-list:")
        energy_int,energy_cnt = measured_scope.energy()
        print(f"integrated: {energy_int}")
        print(f"from counter: {energy_cnt}")

        print("Energy-per-Device-list:")
        energy_int,energy_cnt = measured_scope_sys.energy()
        print(f"integrated: {energy_int}")
        print(f"from counter: {energy_cnt}")

