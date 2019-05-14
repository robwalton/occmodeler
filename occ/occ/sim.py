import dataclasses
import json
import logging
import os
import pathlib
import tempfile
from dataclasses import dataclass

import pandas as pd

import occ.reduction
import pyspike.exe
from occ.model import SystemModel
from pyspike.exe import SimArgs

logging.basicConfig(level=logging.INFO)


# Set default scan location to 'runs' folder in top level of occmodeler dir
BASEDIR = str(pathlib.Path(os.path.abspath(__file__)).parents[2] / 'runs')




# TODO: provide option to create in a lzy way from a run directory
@dataclass
class SimulationResult:
    run: dict  # with keys: dir and optionally num
    model: SystemModel
    sim_args: SimArgs
    places: pd.DataFrame
    transitions: pd.DataFrame
    raw_places: pd.DataFrame
    raw_transitions: pd.DataFrame

    


def run_in_dir(model: SystemModel, sim_args: SimArgs, run_dir) -> SimulationResult:

    assert not os.listdir(run_dir), f"'{run_dir} is not empty'"
    spike_run_dir = os.path.join(run_dir, 'spike')
    os.makedirs(spike_run_dir)

    candl_file_path = model.unit.to_candl_string(model.network, model.network_name)
    spike_manifest_dict = pyspike.exe.run_in_dir(candl_file_path, sim_args, spike_run_dir)

    manifest = {
        'system_model': None,
        'sim_args': dataclasses.asdict(sim_args),
        'spike': dict(spike_manifest_dict)
    }

    with open(os.path.join(run_dir, 'manifest.json'), 'w') as f:
        json.dump(manifest, f, indent=2)

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


def create_simulation_result(model, run_dir=None, run_num=None):

    run_dict = {'dir': run_dir, 'num': run_num}
    with open(os.path.join(run_dir, 'manifest.json'), "r") as read_file:
        manifest = json.load(read_file)
    spike_output_dict = manifest['spike']['output']
    places_path = os.path.join(run_dir, 'spike', spike_output_dict['places'][0])
    raw_places_frame = occ.reduction.read_raw_csv(places_path)
    places_frame = occ.reduction.tidy_places(raw_places_frame)

    transitions_path = os.path.join(run_dir, 'spike', spike_output_dict['transitions'][0])
    raw_transitions_frame = occ.reduction.read_raw_csv(transitions_path)
    transitions_frame = occ.reduction.tidy_transitions(raw_transitions_frame)

    sim_arg_dict = manifest['sim_args']
    sim_args = SimArgs(**sim_arg_dict)
    return SimulationResult(
        run=run_dict, model=model, sim_args=sim_args, places=places_frame, transitions=transitions_frame,
        raw_places=raw_places_frame, raw_transitions=raw_transitions_frame)


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


def load(run_num, basedir=None):
    if not basedir:
        basedir = BASEDIR
    run_dir = os.path.join(basedir, str(run_num))
    if not os.path.exists(run_dir):
        raise ValueError(f"'{run_dir}' does not exist")
    if not os.path.isdir(run_dir):
        raise ValueError(f"'{run_dir}' is not a dir")

    model = None  # Not currently stored
    sr = create_simulation_result(model, run_dir, run_num)
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


# def _write_gml(graph, graph_name, dir):
#     graph_name = graph_name.replace(' ', '-')
#     assert not graph_name.endswith('.gml')
#     medium_path = os.path.join(dir, graph_name + '.gml')
#     nx.write_gml(graph, medium_path, repr)
#     return medium_path