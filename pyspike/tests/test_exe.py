import os
import tempfile

import pyspike.exe


def test_run_in_dir_without_separate_marking():  # m, medium_graph):
    sim_args = pyspike.exe.SimArgs(start=0, stop=1, step=.1, runs=1, repeat_sim=1)
    tmp_dir = tempfile.mkdtemp()

    d = pyspike.exe.run_in_dir(SIMPLE_CANDL_STR, sim_args, tmp_dir)

    assert d['sim_args'] == {'repeat_sim': 1, 'runs': 1, 'start': 0, 'step': 0.1, 'stop': 1}
    assert d['input']['spc'] == 'input/conf.spc'
    assert d['input']['candl'] == 'input/system_model.candl'
    assert d['output'] == {
        'places': ['output/places.csv'],
        'transitions': ['output/transitions.csv']
    }

    with open(os.path.join(tmp_dir, 'output', 'places.csv'), 'r') as f:
        places_str = f.read()
    assert places_str == SIMPLE_CANDLE_PLACES_STR


def test_run_in_dir_without_separate_marking_with_repeat_sim():
    sim_args = pyspike.exe.SimArgs(start=0, stop=1, step=.1, runs=1, repeat_sim=2)
    tmp_dir = tempfile.mkdtemp()

    d = pyspike.exe.run_in_dir(SIMPLE_CANDL_STR, sim_args, tmp_dir)

    assert d['output'] == {
        'places': ['output/places.csv', 'output/places_0000.csv', 'output/places_0001.csv'],
        'transitions': ['output/transitions.csv', 'output/transitions_0000.csv', 'output/transitions_0001.csv']
    }
    for p in d['output']['places']:
        with open(os.path.join(tmp_dir, p), 'r') as f:
            places_str = f.read()
        assert places_str == SIMPLE_CANDLE_PLACES_STR


SIMPLE_CANDLE_PLACES_STR = """Time;b;a;b_0;a_0
0;0;1;0;1
0.1;0;1;0;1
0.2;0;1;0;1
0.3;0;1;0;1
0.4;0;1;0;1
0.5;0;1;0;1
0.6;1;0;1;0
0.7;1;0;1;0
0.8;1;0;1;0
0.9;1;0;1;0
"""

SIMPLE_CANDL_STR = \
"""colspn  [external_transition on two graph]
{
colorsets:
  Unit = {0..2};

variables:
  Unit : u;

colorfunctions:

places:
discrete:
  Unit a = 1`all;
  Unit b = 0`0;

transitions:
deterministic:
  extab
    :
    : [b + {0}] & [a - {0}]
    : 0.5
    ;

}
"""
