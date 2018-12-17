import os.path
import tempfile
import time
from pathlib import Path

import pyspike.sacred.run

import networkx as nx
from sacred import Experiment
from sacred.observers import FileStorageObserver

from pyspike.model import UnitModel
from pyspike.sacred.candl_ingredient import candl_ingredient
from pyspike.sacred.spike_ingredient import spike_ingredient
from pyspike.sacred.visualisation_ingredient import visualisation_ingredient


def run_experiment(unit_model: UnitModel, medium_graph: nx.Graph = None, medium_gml=None, graph_name=None,
                   start=0, stop=10, step=.1, runs=1,
                   archive=False, calling_file: Path = None, file_storage_observer=False):

    """Trigger an experiment in a way that could be done from the bash shell in order
    to ensure repeatability.

    """

    if calling_file:
        assert calling_file.exists()
        assert calling_file.is_file()
        print(f"Resource: '{str(calling_file)}'")
        ex.add_source_file(str(calling_file))

    if file_storage_observer:
        ex.observers.append(FileStorageObserver.create('/Users/walton/Documents/DPhil/proof-of-concept/runs'))

    # with tempfile.TemporaryDirectory() as tmp_dir:
    tmp_dir = tempfile.mkdtemp()

    print('created temporary directory', tmp_dir)
    medium_gml = create_gml_if_necessary(medium_graph, medium_gml, graph_name, tmp_dir)

    candl_path = unit_model.to_candl_file(medium_graph, graph_name, tmp_dir)
    candl_path = str(candl_path)
    print('medium_gml:' + medium_gml)
    print('candl_path:' + candl_path)

    candl_args = dict(candl_template_path='', gml_path='')  # Not using this part so null  out
    spike_args = dict(model_path=candl_path, sim_args=dict(interval=dict(start=start, step=step, stop=stop), runs=runs))
    visualisation_args = dict(enable=True, jupyter_inline=False, medium_gml_path=str(medium_gml))

    # logger = logging.getLogger('my_custom_logger')
    # logger.setLevel(logging.CRITICAL)
    # ex.logger = logger

    return ex.run(config_updates=dict(candl=candl_args, spike=spike_args, visualisation=visualisation_args))


ex = Experiment('Spike run', ingredients=[spike_ingredient, candl_ingredient, visualisation_ingredient])

@ex.automain
def main(candl, spike, visualisation, _log, _run):
    # noinspection PyProtectedMember
    pyspike.sacred.run.main(ex, candl, spike, visualisation, _log, _run._id)


def create_gml_if_necessary(medium_graph, medium_gml, graph_name, tmp_dir):
    # Ensure there is a gml file
    assert medium_graph or medium_gml
    graph_name = graph_name.replace(' ', '-')
    if medium_graph:
        assert not medium_gml
        assert graph_name
        assert not graph_name.endswith('.gml')
        medium_path = os.path.join(tmp_dir, graph_name + '.gml')
        nx.write_gml(medium_graph, medium_path, repr)
        return medium_path
    else:
        return medium_gml












