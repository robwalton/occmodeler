import networkx as nx
import pandas as pd
import pytest
from pandas.util.testing import assert_frame_equal
import matplotlib.pyplot as plt
import plotly.offline as py

from pyspike import temporal, read_csv, tidydata

import os

from pyspike.temporal import generate_place_change_events, generate_transition_events, generate_causal_graph, Occasion

PLOT = True

from tests.files import TRANSITIONS, PLACES


@pytest.fixture
def big_example_frame():
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
    return pd.DataFrame(
        in_rows, columns=['step', 'time', 'type', 'name', 'num', 'count'])


def test_generate_state_change_frame(big_example_frame):


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

    actual_frame = temporal.generate_place_change_events(big_example_frame)
    assert_frame_equal(desired_frame.reset_index(drop=True), actual_frame.reset_index(drop=True))


def test_occasion_repr():

    o = Occasion(unit=1, state='a', time=4.1)
    assert repr(o) == 'a1@4.1'


def test_generate_causal_graph_with_run_77():
    g, place_change_events, transition_events = _load_run_77()

    causal_graph = generate_causal_graph(
        place_change_events, transition_events, 0.1)

    if PLOT:
        nx.draw(causal_graph, with_labels=True)
        plt.show()
    log('actual:', causal_graph.nodes)
    O = Occasion
    desired = [
        O(0, 'a', 0.0), O(1, 'a', 0.0), O(2, 'a', 0.0), O(3, 'a', 0.0), O(4, 'a', 0.0), O(5, 'a', 0.0),
        O(5, 'b', 2.0), O(0, 'b', 1.1), O(4, 'b', 3.0), O(3, 'b', 4.0), O(2, 'b', 5.1), O(1, 'b', 6.1)
    ]
    log('desired:', desired)
    assert list(causal_graph.nodes) == desired


    edge_tuples = list(causal_graph.edges)


    def occ_pair(a, b):
        # s of form a1@0.0
        astate, aunit, atime = a[0], a[1], a[-3:]
        bstate, bunit, btime = b[0], b[1], b[-3:]
        return (Occasion(aunit, astate, atime), Occasion(bunit, bstate, btime))

    desired_edge_tuples = [
        occ_pair('a1@0.0', 'b1@6.1'),
        occ_pair('a2@0.0', 'b2@5.1'),
        occ_pair('a3@0.0', 'b3@4.0'),
        occ_pair('a4@0.0', 'b4@3.0'),
        occ_pair('a5@0.0', 'b5@2.0'),
        occ_pair('b0@1.1', 'b5@2.0'),
        occ_pair('b5@2.0', 'b4@3.0'),
        occ_pair('b4@3.0', 'b3@4.0'),
        occ_pair('b3@4.0', 'b2@5.1'),
        occ_pair('b2@5.1', 'b1@6.1')]

    assert len(edge_tuples) == len(desired_edge_tuples)

    # for desired_edge_tuple in desired_edge_tuples:
    #     assert desired_edge_tuple in edge_tuples



    log('edgess', edge_tuples)
    # TODO: check edges!


class TestCausalPlotting(object):

    @staticmethod
    def _load_graph_77():
        graph_medium, place_change_events, transition_events = _load_run_77()
        causal_graph = generate_causal_graph(
            place_change_events, transition_events, 0.1)
        return causal_graph, graph_medium

    def test_plot_causal_graph_with_run_77(self):
        causal_graph, graph_medium = self._load_graph_77()
        fig = temporal.generate_causal_graph_figure(causal_graph, graph_medium)
        if PLOT:
            url = py.plot(fig)

    def test_extract_state_names(self):
        causal_graph, graph_medium = self._load_graph_77()
        assert temporal.extract_state_names_from_causal_graph(causal_graph) == {'a', 'b'}

    def test_extract_unit_numbers(self):
        causal_graph, graph_medium = self._load_graph_77()
        assert temporal.extract_unit_numbers_from_causal_graph(causal_graph) == set(range(6))

    def test_with_run_71(self):
        # TODO: remove external dependencies
        run_number = 71
        places = read_csv(
            filename=f"/Users/walton/dphil/proof-of-concept/runs/{run_number}/places.csv",
            node_type="place", drop_non_coloured_sums=True)
        transitions = read_csv(
            filename=f"/Users/walton/dphil/proof-of-concept/runs/{run_number}/transitions.csv",
            node_type="transition", drop_non_coloured_sums=True)

        places = tidydata.prepend_tidy_frame_with_tstep(places)
        transitions = tidydata.prepend_tidy_frame_with_tstep(transitions)

        place_change_events = generate_place_change_events(places)
        transition_events = generate_transition_events(transitions)

        causal_graph = generate_causal_graph(
            place_change_events, transition_events, 0.1)
        graph_medium = nx.read_gml(
                "/Users/walton/dphil/proof-of-concept/model/social/notebook/2018-11-22/1.gml",
                destringizer=int)

        fig = temporal.generate_causal_graph_figure(causal_graph, graph_medium)
        if PLOT:
            url = py.plot(fig)






def _load_run_77():
    graph_medium = _gen_loop_graph(6)
    places = read_csv(PLACES, 'place', drop_non_coloured_sums=True)
    places = tidydata.prepend_tidy_frame_with_tstep(places)
    place_change_events = generate_place_change_events(places)
    transitions = read_csv(TRANSITIONS, 'transition', drop_non_coloured_sums=True)
    transitions = tidydata.prepend_tidy_frame_with_tstep(transitions)
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


