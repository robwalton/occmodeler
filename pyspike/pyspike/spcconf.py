import os
import json
import re
from copy import deepcopy
from collections import OrderedDict
from dataclasses import dataclass

from typing import List


@dataclass
class SimArgs:
    start: float
    step: float
    stop: float
    runs: int = 1
    repeat_sim: int = 1


def create_conf_file(model_file_name, sim_args: SimArgs):
    """Create a Spike configuration file (.spc)

    Spike will be run from a working directory containing input and output directories.

    :param model_file_name: name of .candl file in input directory
    :param sim_args: SimArgs
    :return: a list of absolute file paths (as string) which would be written and contents of .spc file to execute with Spike
    """

    assert sim_args.repeat_sim <= 10000  # we will hard code the number of digits to 4 (but start at 0)
    # Make simulation output paths absolute

    # Create spc conf file for Spike

    places_path_list = ['output/places.csv']
    transitions_path_list = ['output/transitions.csv']

    spc_string = create_spc_string(model_file_name, sim_args)

    if sim_args.repeat_sim > 1:
        places_path_list = expand_export_path_list(places_path_list, sim_args.repeat_sim)
        transitions_path_list = expand_export_path_list(transitions_path_list, sim_args.repeat_sim)
    return places_path_list, transitions_path_list,  spc_string


def create_spc_string(model_file_name:str, args: SimArgs) -> str:
    return f'''\
import: {{
    from: "input/system_model.candl";
}}
configuration: {{
    simulation: {{
        name: "unused";
        type: stochastic;
        solver: direct: {{
            threads: 0;
            runs: {args.runs};
        }}
        interval: {args.start}:{args.step}:{args.stop};
        export: {{
            places: [];
            csv: {{
                sep: ";";
                file: "output/places.csv";
            }}
        }}
        export: {{
            transitions: [];
            csv: {{
                sep: ";";
                file: "output/transitions.csv";
            }}
        }}
    }}
}}
'''


def expand_export_path_list(export_path_list, repeat_sim):
    expanded_path_list = []
    for path in export_path_list:
        expanded_path_list.append(path)
        for i in range(repeat_sim):
            expanded_path_list.append(path.replace('.csv', f"_{i:04d}.csv"))
    return expanded_path_list


