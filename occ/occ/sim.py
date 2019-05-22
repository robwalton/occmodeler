import dataclasses
import json
import logging
import os
import pathlib
import tempfile
from dataclasses import dataclass

import networkx as nx
import pandas as pd

import occ.reduction
import pyspike.exe
from occ.model import SystemModel
from pyspike.exe import SimArgs

import occdash.manage



logging.basicConfig(level=logging.INFO)


# Set default scan location to 'runs' folder in top level of occmodeler dir
BASEDIR = str(pathlib.Path(os.path.abspath(__file__)).parents[2] / 'runs')




# TODO: provide option to create in a lzy way from a run directory
@dataclass
class SimulationResult:
    run: dict  # with keys: dir and optionally num
    model: SystemModel
    sim_args: SimArgs
    places: pd.DataFrame  # drop_non_coloured_sums=True
    transitions: pd.DataFrame  # drop_non_coloured_sums=True
    raw_places: pd.DataFrame
    raw_transitions: pd.DataFrame
    # place_sums: pd.DataFrame
    # transition_sums: pd.DataFrame


    def __str__(self):
        s = 'SimulationResult: '
        if 'num' in self.run:
            return s + f"run['num']={self.run['num']}. http://127.0.0.1:8050/run-{self.run['num']}"
        elif 'dir' in self.run:
            return s + f"run['dir']={self.run['dir']}"
        else:
            return s + "temporary run"

    __repr__ = __str__


def run_in_dir(model: SystemModel, sim_args: SimArgs, run_dir) -> SimulationResult:

    # Create dirs
    assert not os.listdir(run_dir), f"'{run_dir} is not empty'"
    spike_run_dir = os.path.join(run_dir, 'spike')
    model_dir = os.path.join(run_dir, 'model')
    os.makedirs(spike_run_dir)
    os.makedirs(model_dir)

    # Move offsets from places onto graph
    assert model.network
    model.network.graph['offsets'] = {}
    for place in model.unit.places:
        assert len(place.pos_offset) == 2
        model.network.graph['offsets'][place.name] = tuple(place.pos_offset)

    # Write model
    medium_path = os.path.join(model_dir, 'medium_graph.gml')
    nx.write_gml(model.network, medium_path, repr)
    system_model = {'unit': None, 'network': 'model/medium_graph.gml',
                    'network_name': model.network_name, 'marking': None}

    # Run spike
    candl_file_path = model.unit.to_candl_string(model.network, model.network_name)
    spike_manifest_dict = pyspike.exe.run_in_dir(candl_file_path, sim_args, spike_run_dir)

    # Create manifest
    manifest = {
        'model': system_model,
        'sim_args': dataclasses.asdict(sim_args),
        'spike': dict(spike_manifest_dict)
    }

    with open(os.path.join(run_dir, 'manifest.json'), 'w') as f:
        json.dump(manifest, f, indent=2)

    occdash.manage.reload_dash_server()

    return create_simulation_result(model, run_dir)


def run_in_tmp(model: SystemModel, sim_args: SimArgs) -> SimulationResult:
    """Call run_in_dir a tmp folder and return results as dataframes.

    :return:
    """
    assert sim_args.repeat_sim == 1  # No use case for this yet

    with tempfile.TemporaryDirectory() as tmp_dir:

        logging.info('Using temporary directory:' + tmp_dir)
        sim_result = run_in_dir(model, sim_args, tmp_dir)
        with open(os.path.join(tmp_dir, 'manifest.json'), "r") as read_file:
            manifest = json.load(read_file)
        spike_output_dict = manifest['spike']['output']
        sim_res = create_simulation_result(model, run_dir=tmp_dir)
        sim_res.run = {}  # Clear as tmp_dir will be gone outside this scope!
        assert sim_res.sim_args == sim_args
        return sim_res



# TODO: move inside SimulationResult
def create_simulation_result(model=None, run_dir=None, run_num=None):

    run_dict = {'dir': run_dir, 'num': run_num}
    with open(os.path.join(run_dir, 'manifest.json'), "r") as read_file:
        manifest = json.load(read_file)

    # Load spike output
    spike_output_dict = manifest['spike']['output']
    places_path = os.path.join(run_dir, 'spike', spike_output_dict['places'][0])
    raw_places_frame = occ.reduction.read_raw_csv(places_path)
    places_frame = occ.reduction.tidy_places(raw_places_frame, drop_non_coloured_sums=True)
    places_frame = occ.reduction.prepend_tidy_frame_with_tstep(places_frame)
    transitions_path = os.path.join(run_dir, 'spike', spike_output_dict['transitions'][0])
    raw_transitions_frame = occ.reduction.read_raw_csv(transitions_path)
    transitions_frame = occ.reduction.tidy_transitions(raw_transitions_frame, drop_non_coloured_sums=True)
    transitions_frame = occ.reduction.prepend_tidy_frame_with_tstep(transitions_frame)

    # model
    if not model:
        network = nx.read_gml(os.path.join(run_dir, 'model', 'medium_graph.gml'), destringizer=int)
        model = SystemModel(unit=None, network=network, network_name=2, marking=None)

    # sim args
    sim_arg_dict = manifest['sim_args']
    sim_args = SimArgs(**sim_arg_dict)
    return SimulationResult(
        run=run_dict, model=model, sim_args=sim_args,
        places=places_frame, transitions=transitions_frame,
        raw_places=raw_places_frame, raw_transitions=raw_transitions_frame)
        # place_sums=place_sums_frame, transition_sums=transition_sums_frame)


def run(model: SystemModel, sim_args: SimArgs, basedir=None):
    """Create a new run directory in basedir and call run_in_dir.
    Returning (run_dir, manifest).
    """
    if not basedir:
        basedir = BASEDIR
    id_ = _IncrementalDir(basedir)
    run_num, run_dir = id_.create_next_dir()
    sim_result = run_in_dir(model, sim_args, run_dir)
    assert sim_result.run['dir'] == run_dir
    sim_result.run['num'] = run_num
    return sim_result


def save(simulation_result: SimulationResult, basedir=None):
    """Archive a SimulationResult as if it were created with run.

    Note, that as the SimulationResult does not include the spike/input files
    these must be regenerated.
    """

    if not basedir:
        basedir = BASEDIR
    sr = simulation_result
    id_ = _IncrementalDir(basedir)
    run_number, archive_dir = id_.create_next_dir()

    assert not os.listdir(archive_dir), f"'{archive_dir} is not empty'"
    spike_run_dir = os.path.join(archive_dir, 'spike')
    os.makedirs(spike_run_dir)

    candl_file_path = sr.model.unit.to_candl_string(sr.model.network, sr.model.network_name)

    # Do everything but run spike
    spike_manifest_dict = pyspike.exe.run_in_dir(candl_file_path, sr.sim_args, spike_run_dir, skip_call=True)

    manifest = {
        'system_model': None,
        'sim_args': dataclasses.asdict(sr.sim_args),
        'spike': dict(spike_manifest_dict)
    }

    with open(os.path.join(archive_dir, 'manifest.json'), 'w') as f:
        json.dump(manifest, f)

    # Write places.csv and transitions.csv
    sr.raw_places.to_csv(os.path.join(spike_run_dir, 'output', 'places.csv'), sep=';', index=False)
    sr.raw_transitions.to_csv(os.path.join(spike_run_dir, 'output', 'transitions.csv'), sep=';', index=False)
    sr.run = {'dir': archive_dir, 'num': run_number}
    return sr


def load(run_num, basedir=None) -> SimulationResult:
    if not basedir:
        basedir = BASEDIR
    run_dir = os.path.join(basedir, str(run_num))
    if not os.path.exists(run_dir):
        raise ValueError(f"'{run_dir}' does not exist")
    if not os.path.isdir(run_dir):
        raise ValueError(f"'{run_dir}' is not a dir")

    sr = create_simulation_result(model=None, run_dir=run_dir, run_num=run_num)
    return sr


class _IncrementalDir(object):
    """Runs the integer number of the next incrementally number dir in basedir.

    Assumes file numbering is contiguous and starting at 0.

    """

    def __init__(self, basedir):
        self.basedir = basedir
        if not os.path.exists(basedir):
            logging.info(f"Creating basedir '{basedir}'")
            os.makedirs(basedir)

    def next_number(self):
        """Finds the next free number in a sequentially named list of files"""
        last_number = self.last_number()
        return 0 if last_number is None else last_number + 1

    def last_number(self):
        """Finds the highest numbered file in a sequentially named list of files
        Return None if no numbered files.
        """
        def num_exists(n):
            return os.path.exists(os.path.join(self.basedir, str(n)))

        if not num_exists(0):
            return None

        i = 0
        while num_exists(i + 1):
            i += 1
        return i

    def create_next_dir(self):
        run_number = self.next_number()
        directory = os.path.join(self.basedir, str(run_number))
        assert not os.path.exists(directory)
        os.makedirs(directory)
        return run_number, directory




# # # Add state offsets to graph and persist with the gml
    # # asert model.network
    # # model.network.graph['offsets'] = {}
    # #
    # # for place in model.unit.places:
    # #     assert len(place.pos_offset) == 2
    # #     model.network.graph['offsets'][place.name] = tuple(place.pos_offset)
    # #
    # # medium_gml = _write_gml(model.network, model.network_name, tmp_dir)
    # # print('medium_gml:' + medium_gml)

    # Create candl file for Spike


