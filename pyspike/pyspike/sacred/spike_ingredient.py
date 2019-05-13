import os
import subprocess

from sacred import Ingredient

import pyspike
import pyspike.sacred
import pyspike.spcconf
from pyspike.sacred import TMP_SPIKE_CONF_PATH, TMP_SPIKE_OUTPUT_DIR


spike_ingredient = Ingredient('spike')


BASE_SIM_ARGS = {
        "name": "blank",
        "type": "stochastic",
        "solver": "direct",
        "threads": 0,
        "interval": {
            "start": 0,
            "step": .1,
            "stop": 10
        },
        "runs": 1,
        "export": [
            {
                "places": [],
                "to": "places.csv"
            },
            {
                "transitions": [],
                "to": "transitions.csv"
            },
        ]
    }

@spike_ingredient.config
def spike_config():

    model_path = ''

    model_args = {}

    sim_args = BASE_SIM_ARGS

    repeat_sim = 1


@spike_ingredient.capture
def prep_for_spike_call(model_path, model_args, sim_args, repeat_sim, _log, _run):
    # Generate contents for conf.spc
    if not model_path:
        raise TypeError("No model_path specified")

    artifact_path_list, spc_string = pyspike.spcconf.create_conf_file(
        model_path, model_args, sim_args, repeat_sim, TMP_SPIKE_OUTPUT_DIR)

    # Prepare Spike input dir
    _create_dirs_if_not_exist(
        [TMP_SPIKE_OUTPUT_DIR, os.path.dirname(TMP_SPIKE_CONF_PATH)], _log)

    _remove_files_if_exist([TMP_SPIKE_CONF_PATH] + artifact_path_list)

    # Write conf file
    with open(TMP_SPIKE_CONF_PATH, 'w') as f:
        f.write(spc_string)

    resource_path_list = [model_path, TMP_SPIKE_CONF_PATH]
    return resource_path_list, artifact_path_list


@spike_ingredient.capture
def call_spike(_log):
    _call_spike(TMP_SPIKE_CONF_PATH, _log)


def _call_spike(conf_path, _log=None):
    args = ["~/bin/spike exe -f {}".format(conf_path)]
    if _log:
        _log.info('Calling: ' + str(args))
    else:
        print('Calling: ' + str(args))
    subprocess.run(args, shell=True)  # check=True)
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



def _create_dirs_if_not_exist(path_list, _log):
    for path in path_list:
        if not os.path.exists(path):
            _log.info(f'Creating: {path}')
            os.makedirs(path)


def _remove_files_if_exist(path_list):
    for path in path_list:
        try:
            os.remove(path)
        except FileNotFoundError:
            pass









