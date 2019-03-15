from pathlib import Path

import networkx as nx
from matplotlib import pyplot as plt
import numpy as np

from pyspike.sacred import call
import os
from pathlib import Path

import pyspike
from pyspike import tidydata
from model import FollowNeighbour as follow1, FollowTwoNeighbours as follow2, ModulatedInternal as modulated_internal
from pyspike.model import UnitModel, u, n1, n2, Unit
from pyspike.model import marking
import plotly.offline as py
import plotly.graph_objs as go

import pyspike
from pyspike import tidydata
import pyspike.util

from pyspike.util import render_name


import websci19
import websci19.models


def sym_bar_like_network(nodes_per_half=7, seed_a=1, seed_b=2):
    """Symmetrical bar bell like network"""
    a = nx.newman_watts_strogatz_graph(nodes_per_half, 4, 0.1, seed=seed_a)
    b = nx.newman_watts_strogatz_graph(nodes_per_half, 4, 0.1, seed=seed_b)
    G = nx.compose(a, nx.convert_node_labels_to_integers(b, first_label=nodes_per_half))
    G.add_edge(nodes_per_half - 1, nodes_per_half);
    # nx.draw_kamada_kawai(G)
    # plt.show()
    return G


def network():
    G = sym_bar_like_network()
    assert G.number_of_nodes() == 14

    pos = {
        0: {'pos': [0.69217614, -0.08936685]},
        1: {'pos': [0.88684588, -0.21683806]},
        2: {'pos': [0.74811776, -0.361906]},
        3: {'pos': [0.88586679, -0.57842461]},
        4: {'pos': [0.56674439, -0.59722088]},
        5: {'pos': [0.5637971, -0.39880716]},
        6: {'pos': [0.36828676, -0.16369905]},
        7: {'pos': [0., 0.]},
        8: {'pos': [-0.29597752, 0.08424162]},
        9: {'pos': [-0.45945856, -0.08909171]},
        10: {'pos': [-0.65118034, 0.17981018]},
        11: {'pos': [-0.40931661, 0.1908196]},
        12: {'pos': [-0.33473102, 0.35073648]},
        13: {'pos': [-0.11943313, 0.32944159]}
    }
    nx.set_node_attributes(G, pos)
    return G


def plot_network(medium_graph=None):
    if medium_graph:
        nx.draw(medium_graph)
        plt.show()
    else:
        G = network()
        nx.draw(G, pos=nx.get_node_attributes(G, 'pos'))
        plt.show()

def n_nodes():
    return network().number_of_nodes()

def run_on_network(
        model, medium_graph=None, graph_name='two community',
        start=0, stop=10, step=.01, runs=1, repeat_sim=1,
        save_run=False):
    if not medium_graph:
        medium_graph = network()
    return call.run_experiment(
        model, medium_graph=medium_graph, graph_name=graph_name,
        start=start, stop=stop, step=step, runs=runs, repeat_sim=repeat_sim,
        calling_file=Path(__file__), file_storage_observer=save_run)




# All should return link to causal graph

def mock_experiment():
    """Returns link to run 136

    """
    return "/Users/walton/Documents/DPhil/proof-of-concept/runs/136/causal_graph.html"


# DIFFUSION

def diffusion(save_run=False):
    """From one end"""
    indexes = list(range(n_nodes()))
    launch_node = 0
    indexes.remove(launch_node)
    a = Unit.place('a', marking(indexes))
    b = Unit.place('b', marking([launch_node]))
    m = UnitModel(name="diffusion", colors=[Unit], variables=[u, n1, n2],
                  places=[a, b])
    m.add_transitions_from([
        follow1(a, b, use_read_arc=False)
    ])
    return run_on_network(m, save_run=save_run)

def multiphase_diffusion(save_run=False):
    indexes = list(range(n_nodes()))
    for i in [5, 4, 3]:
        indexes.remove(i)

    a = Unit.place('a', marking(indexes))
    b = Unit.place('b', marking([4, 3]))
    c = Unit.place('c', marking([5]))
    m = UnitModel(name="multiphase_diffusion", colors=[Unit], variables=[u, n1, n2],
                  places=[a, b])
    m.add_transitions_from([
        follow1(a, b),
        follow1(b, c)
    ])
    medium_graph = nx.newman_watts_strogatz_graph(14, 4, 0.2, seed=5)
    return run_on_network(m, medium_graph=medium_graph, save_run=save_run)

def two_neighbour_diffusion(save_run=False):
    indexes = list(range(n_nodes()))
    init1 = 3
    init2 = 4

    indexes.remove(init1)
    indexes.remove(init2)

    a = Unit.place('a', marking(indexes))
    b = Unit.place('b', marking([init1, init2]))
    m = UnitModel(name="two_neighbour_diffusion", colors=[Unit], variables=[u, n1, n2],
                  places=[a, b])
    m.add_transitions_from([
        follow2(a, b, 1),
    ])
    return run_on_network(m, save_run=save_run)



def one_plus_two_neighbour_diffusion(save_run=False):
    indexes = list(range(n_nodes()))
    init1 = 3
    init2 = 4

    indexes.remove(init1)
    indexes.remove(init2)

    a = Unit.place('a', marking(indexes))
    b = Unit.place('b', marking([init1, init2]))
    m = UnitModel(name="one_plus_two_neighbour_diffusion", colors=[Unit], variables=[u, n1, n2],
                  places=[a, b])
    m.add_transitions_from([
        follow2(a, b, 1),
        follow1(a, b, .5),
    ])
    return run_on_network(m, save_run=save_run)

# CONSENSUS

def single_issue_consensus(save_run=False):  # From noise with 1 and 2 neighbours
    a, A = websci19.models.generate_pair_with_random_markings('a', 'A', n_nodes())
    m = UnitModel(name="single_issue_consensus", colors=[Unit], variables=[u, n1, n2],
                  places=[a, A])
    m.add_transitions_from([
        follow1(a, A, .5),
        follow1(A, a, .5),
        follow2(a, A, 1),
        follow2(A, a, 1),
    ])
    return run_on_network(m, save_run=save_run)

def community_resilience_with_one_determined_neighbour(save_run=False):
    pass
    # Not required as single_issue_consensus showed stability

# CONFLATION

def triangle_coords_around_zero(edge_width):
    a = (-.5 * edge_width, -edge_width * .866 / 2)
    b = (.5 * edge_width, -edge_width * .866 / 2)
    c = (0 * edge_width, edge_width * 0.866 / 2)
    return a, b, c

def conflation_through_emotion(save_run=False):

    a_off, b_off, e_off = triangle_coords_around_zero(.05)
    a, A = websci19.models.generate_pair_with_random_markings('a', 'A', n_nodes(), pos_offset=a_off)
    b, B = websci19.models.generate_pair_with_random_markings('b', 'B', n_nodes(), pos_offset=b_off)
    e, E = websci19.models.generate_pair_with_marking('e', 'E', n_nodes(), list(range(int(n_nodes() / 2))), pos_offset=e_off)

    m = UnitModel(name="conflation_through_emotion", colors=[Unit], variables=[u, n1, n2],
                  places=[a, A, b, B, e, E])

    r_f1 = 1
    r_f2 = 2
    r_e_f1 = r_f1
    r_e_f2 = r_f2
    r_ab_to_e = 1

    m.add_transitions_from([
        follow1(a, A, r_f1, enabled_by_local=E),
        follow1(A, a, r_f1, enabled_by_local=e),
        # follow2(a, A, r_f2, enabled_by_local=E),
        # follow2(A, a, r_f2, enabled_by_local=e),
        follow1(b, B, r_f1, enabled_by_local=E),
        follow1(B, b, r_f1, enabled_by_local=e),
        # follow2(b, B, r_f2, enabled_by_local=E),
        # follow2(B, b, r_f2, enabled_by_local=e),
        follow1(e, E, r_e_f1),
        follow1(E, e, r_e_f1),
        # follow2(e, E, r_e_f2),
        # follow2(E, e, r_e_f2),
        modulated_internal(A, a, e, rate=r_ab_to_e),
        modulated_internal(B, b, e, rate=r_ab_to_e),
        modulated_internal(a, A, E, rate=r_ab_to_e),
        modulated_internal(b, B, E, rate=r_ab_to_e),
    ])
    return run_on_network(m, save_run=save_run)


def run_all_experiments_and_save():
    rl = []  # report lines
    for f in [diffusion]: #, multiphase_diffusion, two_neighbour_diffusion, one_plus_two_neighbour_diffusion,
              #single_issue_consensus, conflation_through_emotion]:
        run = f(save_run=True)
        rl.append(f.__name__ + str(run._id))

    print('\n'.join(rl))
