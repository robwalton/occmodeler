from pyspike.spcconf import create_conf_file

from pyspike.tidydata import read_csv

import subprocess


def call_spike(conf_path):
    args = ["spike exe -f {}".format(conf_path)]
    print('Calling: ' + str(args))
    subprocess.run(args, shell=True) # check=True)
    # spike 1.0.1 always returns error code 1. Reported on 2018/11/2.
    # try:
    #     subprocess.run(["spike help", "-c", "prune"], shell=True, check=True)
    # except subprocess.CalledProcessError as e:
    #     print('!' * 10)
    #     print('cmd: ' + str(e.cmd))
    #     print('returncode: ' + str(e.returncode))
    #     print('stdout: ' + (e.stdout if e.stdout else 'NONE'))
    #     print('stderr: ' + (e.stderr if e.stderr else 'NONE'))
    #     print('output: ' + (e.output if e.output else 'NONE'))
    #     print('!' * 10)
    #     raise e


__all__ = ["call_spike", "read_csv", "create_conf_file"]
