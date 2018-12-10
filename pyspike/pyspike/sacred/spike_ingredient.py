import os

from sacred import Ingredient

import pyspike
import pyspike.sacred
from pyspike.sacred import TMP_SPIKE_CONF_PATH, TMP_SPIKE_OUTPUT_DIR


spike_ingredient = Ingredient('spike')


@spike_ingredient.config
def spike_config():

    model_path = ''

    model_args = {}

    sim_args = {
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

    repeat_sim = 1


@spike_ingredient.capture
def prep_for_spike_call(model_path, model_args, sim_args, repeat_sim, _log, _run):
    # Generate contents for conf.spc
    if not model_path:
        raise TypeError("No model_path specified")

    artifact_path_list, spc_string = pyspike.create_conf_file(
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
    pyspike.call_spike(TMP_SPIKE_CONF_PATH, _log)


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









