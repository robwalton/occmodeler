import networkx as nx
from pathlib import Path

from pyspike.sacred import call


MEDIUM_GRAPH = nx.read_gml(Path(__file__).parent / 'tos-network.gml', destringizer=int)


assert MEDIUM_GRAPH.number_of_nodes() == 30

def create_run_on_tos_network_function(_calling_file):

    def run_on_tos_network(
            model, medium_graph=MEDIUM_GRAPH, graph_name='tos network',
            start=0, stop=20, step=.1, runs=1, repeat_sim=1,
            calling_file=_calling_file, save_run=False):
        return call.run_experiment(
            model, medium_graph=medium_graph, graph_name=graph_name,
            start=start, stop=stop, step=step, runs=runs,  repeat_sim=repeat_sim,
            calling_file=calling_file, file_storage_observer=save_run)

    return run_on_tos_network
