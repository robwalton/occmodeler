import dataclasses
import logging
import os
import subprocess
from dataclasses import dataclass

import pyspike.spcconf

logging.basicConfig(level=logging.INFO)

CANDL_FILE_NAME = 'system_model.candl'


@dataclass
class SimArgs:
    start: float
    step: float
    stop: float
    runs: int
    repeat_sim: int


def run_in_dir(candl_str: str, sim_args: SimArgs, spike_run_dir):
    """Run spike in a given directory returning a manifest dictionary.

    Creates:

        input/conf.spc
        input/system_model.candl
        output/... (places and transitions csv files)
    """

    places_path_list, transitions_path_list, relative_spc_path, candl_path = \
        _prep_for_spike_call(candl_str, sim_args, spike_run_dir)

    call_spike(spike_run_dir, relative_spc_path)

    spike_manifest = {

        'input': {
            'candl': candl_path,
            'spc': relative_spc_path

        },
        'output': {
            'places': places_path_list,
            'transitions': transitions_path_list
        }

    }
    return spike_manifest


def _prep_for_spike_call(candl_string: str, sim_args: SimArgs, spike_run_dir):
    """
    Creates `run_dir/input` containing the .candl and .spc files required to call Spike. Spike will write to created `run_dir/output`.
    :param candl_string:
    :param sim_args:
    :param run_dir: should be empty
    :return: path to .spc to call spike with
    """

    assert not os.listdir(spike_run_dir), f"'{spike_run_dir} is not empty'"

    # Create input and output dirs in run_dir
    run_dir_input = os.path.join(spike_run_dir, 'input')  # path for input to Spike call
    run_dir_output = os.path.join(spike_run_dir, 'output')  # path for output from Spike call
    os.makedirs(run_dir_input)
    os.makedirs(run_dir_output)


    with open(os.path.join(run_dir_input, CANDL_FILE_NAME), 'w') as f:
        f.write(candl_string)

    # Create spc conf file for Spike

    spike_model_args = {}
    spike_sim_args = {
        "name": "Diffusion",
        "type": "stochastic",
        "solver": "direct",
        "threads": 0,
        "interval": {
            "start": sim_args.start,
            "step": sim_args.step,
            "stop": sim_args.stop,
        },
        "runs": sim_args.runs,
        "export": [
            {
                "places": [],
                "to": "output/places.csv"
            },
            {
                "transitions": [],
                "to": "output/transitions.csv"
            }
        ]
    }
    places_path_list, transitions_path_list, spc_string = pyspike.spcconf.create_conf_file(
        CANDL_FILE_NAME, spike_model_args, spike_sim_args, sim_args.repeat_sim)

    # Write conf file
    spc_path = os.path.join(run_dir_input, 'conf.spc')
    with open(spc_path, 'w') as f:
        f.write(spc_string)

    return (places_path_list, transitions_path_list,
            'input/conf.spc', os.path.join('input', CANDL_FILE_NAME))


def call_spike(working_dir, spc_path):
    assert os.path.isfile(os.path.join(working_dir, spc_path))
    args = ["~/bin/spike exe -f {}".format(spc_path)]
    logging.info(f"Calling: '{str(args)}' from cwd: {working_dir}")
    subprocess.run(args, cwd=working_dir, shell=True)  # check=True)

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