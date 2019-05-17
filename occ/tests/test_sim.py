import json
import os
from io import StringIO

import networkx as nx
import pandas as pd
import pytest

from occ.model import Unit, UnitModel, ext, u, SystemModel
from occ.sim import SimArgs, run_in_dir, run_in_tmp, run, save, load, _IncrementalDir
import occ.sim

@pytest.fixture
def a():
    return Unit.place('a', '1`all')


@pytest.fixture
def b():
    return Unit.place('b')


@pytest.fixture
def m(a, b):
    m = UnitModel(
        name='external_transition',
        colors=[Unit],
        variables=[u],
        places=[a, b]
    )
    m.add_transitions_from([
        ext(a, b, 0.5, [0]),  # transition node 0 at .5 s
    ])
    return m


@pytest.fixture
def medium_graph():
    return nx.Graph([(0, 1), (1, 2)])


@pytest.fixture
def sim_args():
    return SimArgs(start=0, stop=1, step=.1, runs=1, repeat_sim=1)


@pytest.fixture
def model(m, medium_graph):
    return SystemModel(m, medium_graph, 'two graph', None)


@pytest.fixture
def incremental_dir(tmp_path):
    return _IncrementalDir(tmp_path)



# TODO: Erroneously runs setup for each method!
class TestRunInDir:

    @pytest.fixture(autouse=True)  # , scope='class')
    def setup(self, model, sim_args, tmpdir):
        self.rundir = tmpdir.strpath
        self.sim_res = run_in_dir(model, sim_args, tmpdir)

    def test_ran_at_all(self):
        assert self.sim_res  # is not none

    def test_simres_run(self):
        assert self.sim_res.run['dir'] == self.rundir
        assert self.sim_res.run['num'] is None

    def test_manifiset(self):
        with open(os.path.join(self.rundir, 'manifest.json'), "r") as read_file:
            manifest = json.load(read_file)
        d = manifest
        assert d['system_model'] is None  # Placeholder
        assert d['sim_args'] == {'repeat_sim': 1, 'runs': 1, 'start': 0, 'step': 0.1, 'stop': 1}
        assert d['spike']['input']['spc'] == 'input/conf.spc'
        assert d['spike']['input']['candl'] == 'input/system_model.candl'
        assert d['spike']['output'] == {
            'places': ['output/places.csv'],
            'transitions': ['output/transitions.csv']
        }

    def test_spike_output(self):
        with open(os.path.join(self.rundir, 'spike', 'output', 'places.csv'), 'r') as f:
            places_str = f.read()
        assert places_str == SIMPLE_CANDLE_PLACES_STR


def test_run_in_tmp_dir(model, sim_args):
    sr = run_in_tmp(model, sim_args)
    assert sr.sim_args == sim_args
    assert sr.model == model
    assert 'num' not in sr.run
    assert 'dir' not in sr.run
    desired_places = pd.read_csv(StringIO(SIMPLE_CANDLE_PLACES_STR), sep=";")
    pd.testing.assert_frame_equal(sr.raw_places, desired_places)
    assert sr.places is not None  # lazy!


def test_run_in_next_dir(model, sim_args, tmp_path):
    base_dir = tmp_path
    sr = run(model, sim_args, base_dir)

    assert sr.run['num'] == 0
    assert sr.run['dir'] == os.path.join(tmp_path, str(0))
    manifest_dir = os.path.join(tmp_path, str(0), 'manifest.json')
    assert os.path.isfile(manifest_dir)


def test_simulation_result_to_string(model, sim_args, tmp_path):
    base_dir = tmp_path
    sr = run(model, sim_args, base_dir)


def test_get_default_basedir():
    print(occ.sim.BASEDIR)


def test_load(model, sim_args, tmp_path):
    expected = run(model, sim_args, tmp_path)
    actual = load(0, tmp_path)
    assert expected.run == actual.run
    # assert expected.model == actual.model  # model not currently stored!
    assert expected.sim_args == actual.sim_args
    pd.testing.assert_frame_equal(expected.places, actual.places)
    pd.testing.assert_frame_equal(expected.transitions, actual.transitions)
    pd.testing.assert_frame_equal(expected.raw_places, actual.raw_places)
    pd.testing.assert_frame_equal(expected.raw_transitions, actual.raw_transitions)


class TestArchiveInNextDir:

    @pytest.fixture(autouse=True)
    def setup(self, model, sim_args, tmpdir):
        self.basedir = tmpdir.strpath
        sr = run_in_tmp(model, sim_args)
        assert 'num' not in sr.run
        assert 'dir' not in sr.run

        self.sim_res = save(sr, self.basedir)
        self.rundir = os.path.join(self.basedir, str(0))

    def test_ran_at_all(self):
        assert self.sim_res  # is not none

    def test_simres_run(self):
        assert self.sim_res.run['dir'] == self.rundir
        assert self.sim_res.run['num'] == 0

    def test_manifiset(self):
        with open(os.path.join(self.rundir, 'manifest.json'), "r") as read_file:
            manifest = json.load(read_file)
        d = manifest
        assert d['system_model'] is None  # Placeholder
        assert d['sim_args'] == {'repeat_sim': 1, 'runs': 1, 'start': 0, 'step': 0.1, 'stop': 1}
        assert d['spike']['input']['spc'] == 'input/conf.spc'
        assert d['spike']['input']['candl'] == 'input/system_model.candl'
        assert d['spike']['output'] == {
            'places': ['output/places.csv'],
            'transitions': ['output/transitions.csv']
        }

    def test_spike_output(self):
        with open(os.path.join(self.rundir, 'spike', 'output', 'places.csv'), 'r') as f:
            places_str = f.read()
        assert places_str == SIMPLE_CANDLE_PLACES_STR_WITH_TSTEP_0_INCLUDING_DECIMAL


class TestIncrementalDir:

    def test_incremental_dir_when_empty(self, incremental_dir):
        id_ = incremental_dir
        assert id_.last_number() is None
        assert id_.next_number() == 0

    def test_incremental_dir_first_next_dir(self, incremental_dir):
        id_ = incremental_dir

        run_num, d = id_.create_next_dir()
        assert run_num == 0
        assert d == os.path.join(id_.basedir, str(0))
        assert os.path.exists(d)
        assert id_.last_number() == 0
        assert id_.next_number() == 1

        run_num, d = id_.create_next_dir()
        assert d == os.path.join(id_.basedir, str(1))
        assert os.path.exists(d)
        assert id_.last_number() == 1
        assert id_.next_number() == 2

    def test_incremental_dir_second_next_dir(self, incremental_dir):
        id_ = incremental_dir

        id_.create_next_dir()
        run_num, run_dir = id_.create_next_dir()
        assert run_dir == os.path.join(id_.basedir, str(1))
        assert os.path.exists(run_dir)
        assert id_.last_number() == 1
        assert id_.next_number() == 2


def test_dataframe_to_csv():
    # Just experimenting
    places = pd.read_csv(StringIO(SIMPLE_CANDLE_PLACES_STR), sep=";")
    places_csv_str = places.to_csv(sep=';', index=False)  # <===
    print(places_csv_str)
    assert places_csv_str == SIMPLE_CANDLE_PLACES_STR_WITH_TSTEP_0_INCLUDING_DECIMAL


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

SIMPLE_CANDLE_PLACES_STR_WITH_TSTEP_0_INCLUDING_DECIMAL = """Time;b;a;b_0;a_0
0.0;0;1;0;1
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

