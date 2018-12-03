import networkx as nx
import pandas as pd
from pandas.util.testing import assert_frame_equal
import matplotlib.pyplot as plt

from pyspike import temporal, read_csv

import os

from pyspike.temporal import generate_place_change_events, generate_transition_events, generate_causal_graph, Occasion

PLOT = True

THIS_DIR = os.path.dirname(os.path.realpath(__file__))
TEMPORAL = os.path.join(THIS_DIR, 'files', 'temporal')
PLACES = os.path.join(TEMPORAL, 'places.csv')
TRANSITIONS = os.path.join(TEMPORAL, 'transitions.csv')


def test_generate_state_change_frame():
    in_rows = [
        # step, time, type, name, num, count
        [0, 0., 'place', 'a', 1, 1],
        [0, 0., 'place', 'a', 2, 1],
        [0, 0., 'place', 'b', 1, 0],
        [0, 0., 'place', 'b', 2, 0],
        #
        [1, 1., 'place', 'a', 1, 1],
        [1, 1., 'place', 'a', 2, 1],
        [1, 1., 'place', 'b', 1, 0],
        [1, 1., 'place', 'b', 2, 0],
        #
        [2, 2., 'place', 'a', 1, 0],
        [2, 2., 'place', 'a', 2, 1],
        [2, 2., 'place', 'b', 1, 1],
        [2, 2., 'place', 'b', 2, 0],
        #
        [3, 3., 'place', 'a', 1, 0],
        [3, 3., 'place', 'a', 2, 0],
        [3, 3., 'place', 'b', 1, 1],
        [3, 3., 'place', 'b', 2, 1],
        #
        [4, 4., 'place', 'a', 1, 1],
        [4, 4., 'place', 'a', 2, 0],
        [4, 4., 'place', 'b', 1, 0],
        [4, 4., 'place', 'b', 2, 1],
    ]
    in_frame = pd.DataFrame(
        in_rows, columns=['step', 'time', 'type', 'name', 'num', 'count'])

    desired_rows = [
        # 'step', 'time', 'type', 'name', 'num']
        [0, 0., 'place', 'a', 1],
        [0, 0., 'place', 'a', 2],
        [2, 2., 'place', 'b', 1],
        [3, 3., 'place', 'b', 2],
        [4, 4., 'place', 'a', 1],

    ]
    desired_frame = pd.DataFrame(
        desired_rows, columns=['step', 'time', 'type', 'name', 'num'])

    desired_frame = desired_frame.sort_values(by=['time', 'num'])
    desired_frame['num'] = pd.to_numeric(desired_frame['num'], downcast='integer')

    actual_frame = temporal.generate_place_change_events(in_frame)
    assert_frame_equal(desired_frame.reset_index(drop=True), actual_frame.reset_index(drop=True))


def test_occasion_repr():

    o = Occasion(unit=1, state='a', time=4.1)
    assert repr(o) == 'a1@4.1'


def test_generate_causal_graph_with_run_77():
    g, place_change_events, transition_events = _load_run_77()

    causal_graph = generate_causal_graph(
        place_change_events, transition_events)

    if PLOT:
        nx.draw(causal_graph, with_labels=True)
        plt.show()
    log(causal_graph.nodes)
    assert list(causal_graph.nodes) == [
        (0, 'a', 0.0), (1, 'a', 0.0), (2, 'a', 0.0), (3, 'a', 0.0), (4, 'a', 0.0), (5, 'a', 0.0),
        (0, 'b', 1.1), (5, 'b', 2.0), (4, 'b', 3.0), (3, 'b', 4.0), (2, 'b', 5.1), (1, 'b', 6.1)
    ]
    log('edges', g.edges)
    # TODO: check edges!


class TestCausalPlotting(object):

    @staticmethod
    def _load_graph_77():
        graph_medium, place_change_events, transition_events = _load_run_77()
        causal_graph = generate_causal_graph(
            place_change_events, transition_events)
        return causal_graph, graph_medium

    def test_plot_causal_graph_with_run_77(self):
        causal_graph, graph_medium = self._load_graph_77()
        if PLOT:
            temporal.plot_causal_graph(causal_graph, graph_medium)

    def test_extract_state_names(self):
        causal_graph, graph_medium = self._load_graph_77()
        assert temporal.extract_state_names_from_causal_graph(causal_graph) == {'a', 'b'}

    def test_extract_unit_numbers(self):
        causal_graph, graph_medium = self._load_graph_77()
        assert temporal.extract_unit_numbers_from_causal_graph(causal_graph) == set(range(6))

    def test_with_run_71(self):

        run_number = 71
        places = read_csv(
            filename=f"/Users/walton/dphil/proof-of-concept/runs/{run_number}/places.csv",
            node_type="place", drop_non_coloured_sums=True)
        transitions = read_csv(
            filename=f"/Users/walton/dphil/proof-of-concept/runs/{run_number}/transitions.csv",
            node_type="transition", drop_non_coloured_sums=True)

        place_change_events = generate_place_change_events(places)
        transition_events = generate_transition_events(transitions)

        causal_graph = generate_causal_graph(
            place_change_events, transition_events)
        medium_graph = nx.read_gml(
                "/Users/walton/dphil/proof-of-concept/model/social/notebook/2018-11-22/1.gml",
                destringizer=int)

        if PLOT:
            temporal.plot_causal_graph(causal_graph, medium_graph)






def _load_run_77():
    graph_medium = _gen_loop_graph(6)
    places = read_csv(PLACES, 'place', drop_non_coloured_sums=True)
    place_change_events = generate_place_change_events(places)
    transitions = read_csv(TRANSITIONS, 'transition', drop_non_coloured_sums=True)
    transition_events = generate_transition_events(transitions)
    return graph_medium, place_change_events, transition_events


def _gen_loop_graph(n):
    g = nx.Graph()
    for i in range(n-1):
        g.add_edge(i, i+1)
    g.add_edge(n-1, 0)
    return g


def log(*thing_list):
    print('---')
    for thing in thing_list:
        print(thing)
    print('---')


