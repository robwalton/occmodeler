import networkx as nx
import pandas as pd
from pandas.util.testing import assert_frame_equal
import matplotlib.pyplot as plt

from pyspike import temporal, read_csv

import os

from pyspike.temporal import generate_place_change_events, generate_transition_events, generate_causal_graph

PLOT = False

THIS_DIR = os.path.dirname(os.path.realpath(__file__))
TEMPORAL = os.path.join(THIS_DIR, 'files', 'temporal')
PLACES = os.path.join(TEMPORAL, 'places.csv')
TRANSITIONS = os.path.join(TEMPORAL, 'transitions.csv')


def _gen_loop_graph(n):
    g = nx.Graph()
    for i in range(1, n):
        g.add_edge(i, i+1)
    g.add_edge(n, 1)
    return g


def log(thing):
    print('---')
    print(thing)
    print('---')


g = _gen_loop_graph(6)
log(g)

places = read_csv(PLACES, 'place', drop_non_coloured_sums=True)
place_change_events = generate_place_change_events(places)

transitions = read_csv(TRANSITIONS, 'transition', drop_non_coloured_sums=True)
transition_events = generate_transition_events(transitions)
log(place_change_events)
log(transition_events)
causal_graph = generate_causal_graph(
    place_change_events, transition_events)
if PLOT:
    nx.draw(causal_graph, with_labels=True)
    plt.show()
