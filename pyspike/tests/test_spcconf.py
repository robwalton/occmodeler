import json
import os
import tempfile

import pyspike.spcconf


###########
INTEGRATION_FILE_NAME = 'system_model.candl'
INTEGRATION_SIM_ARGS = pyspike.spcconf.SimArgs(0, 0.1, 10, 1, 1)
INTEGRATION_SIM_ARGS_2_SIMS = pyspike.spcconf.SimArgs(0, 0.1, 10, 1, 2)

INTEGRATION_SPC_STRING = '''\
import: {
    from: "input/system_model.candl";
}
configuration: {
    simulation: {
        name: "unused";
        type: stochastic;
        solver: direct: {
            threads: 0;
            runs: 1;
        }
        interval: 0:0.1:10;
        export: {
            places: [];
            csv: {
                sep: ";";
                file: "output/places.csv";
            }
        }
        export: {
            transitions: [];
            csv: {
                sep: ";";
                file: "output/transitions.csv";
            }
        }
    }
}
'''


def test_create_spc_string():
    s = pyspike.spcconf.create_spc_string(INTEGRATION_FILE_NAME, INTEGRATION_SIM_ARGS)
    assert s == INTEGRATION_SPC_STRING


def test_expand_export_path_list():
    epl = ['o/places.csv', 'o/transitions.csv']
    expanded_epl = pyspike.spcconf.expand_export_path_list(epl, 3)
    print('**')
    print(expanded_epl)
    print('**')
    assert expanded_epl == [
        'o/places.csv',
        'o/places_0000.csv',
        'o/places_0001.csv',
        'o/places_0002.csv',
        'o/transitions.csv',
        'o/transitions_0000.csv',
        'o/transitions_0001.csv',
        'o/transitions_0002.csv',
    ]


def test_create_conf_file():
    places_path_list, transitions_path_list,  spc_string = pyspike.spcconf.create_conf_file(
        'empty.candl', INTEGRATION_SIM_ARGS)
    assert places_path_list == ['output/places.csv']
    assert transitions_path_list == ['output/transitions.csv']


def test_create_conf_file_with_multiple_runs():
    places_path_list, transitions_path_list,  spc_string = pyspike.spcconf.create_conf_file(
        'empty.candl', INTEGRATION_SIM_ARGS_2_SIMS)
    assert places_path_list == ['output/places.csv', 'output/places_0000.csv', 'output/places_0001.csv']
    assert transitions_path_list == ['output/transitions.csv', 'output/transitions_0000.csv', 'output/transitions_0001.csv']


