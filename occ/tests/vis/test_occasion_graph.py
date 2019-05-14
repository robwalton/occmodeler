import networkx as nx
import plotly.offline as py

import occ.reduction.occasion_graph
import occ.reduction.read
from occ.reduction import read
from occ.vis import occasion_graph

from occ.vis.occasion_graph import Style
from occ.reduction.occasion_graph import generate_place_increased_events, generate_transition_events, \
    generate_causal_graph

from occ_test_files import TRANSITIONS, PLACES
import occ_test_files


PLOT = True


class TestCausalPlotting(object):

    @staticmethod
    def _load_graph_77():
        graph_medium, place_change_events, transition_events = _load_run_77()
        causal_graph = generate_causal_graph(
            place_change_events, transition_events, 0.1)
        return causal_graph, graph_medium

    def test_plot_causal_graph_with_run_77(self):
        causal_graph, graph_medium = self._load_graph_77()
        fig = occasion_graph.generate_causal_graph_figure(causal_graph, graph_medium)
        if PLOT:
            url = py.plot(fig)

    def test_extract_state_names(self):
        causal_graph, graph_medium = self._load_graph_77()
        assert occ.reduction.occasion_graph.extract_state_names_from_causal_graph(causal_graph) == {'a', 'b'}

    def test_extract_unit_numbers(self):
        causal_graph, graph_medium = self._load_graph_77()
        assert occ.reduction.occasion_graph.extract_unit_numbers_from_causal_graph(causal_graph) == set(range(6))

    def test_with_run_71(self):

        places = read.read_tidy_csv(
            filename=occ_test_files.files.RUN_71_PLACES,
            node_type="place", drop_non_coloured_sums=True)
        transitions = read.read_tidy_csv(
            filename=occ_test_files.files.RUN_71_TRANSITIONS,
            node_type="transition", drop_non_coloured_sums=True)
        graph_medium = nx.read_gml(
            occ_test_files.files.RUN_71_NETWORK_GML,
            destringizer=int)

        places = occ.reduction.read.prepend_tidy_frame_with_tstep(places)
        transitions = occ.reduction.read.prepend_tidy_frame_with_tstep(transitions)

        place_change_events = generate_place_increased_events(places)
        transition_events = generate_transition_events(transitions)

        causal_graph = generate_causal_graph(
            place_change_events, transition_events, 0.1)

        fig = occasion_graph.generate_causal_graph_figure(causal_graph, graph_medium, style=Style.ORIG)
        if PLOT:
            url = py.plot(fig)
            print(url)

    def test_with_run_90(self):
        graph_medium, place_change_events, transition_events = _load_run_90()
        causal_graph = generate_causal_graph(
            place_change_events, transition_events, 0.1)
        fig = occasion_graph.generate_causal_graph_figure(causal_graph, graph_medium)
        if PLOT:
            url = py.plot(fig)
            print(url)

    def test_with_run_100(self):
        graph_medium, place_change_events, transition_events = _load_run_100()
        causal_graph = generate_causal_graph(
            place_change_events, transition_events, 0.1)
        fig = occasion_graph.generate_causal_graph_figure(causal_graph, graph_medium)
        if PLOT:
            url = py.plot(fig)
            print(url)
        raise AssertionError("Missing transitions at 2s (or 2.1) for ")


# TODO: Remove duplication here and in pyspike.tests.files.__init__

def _load_run_90():
    graph_medium = nx.read_gml(occ_test_files.files.RUN_90_GML, destringizer=int)
    places = read.read_tidy_csv(occ_test_files.files.RUN_90_PLACES, 'place', drop_non_coloured_sums=True)
    places = occ.reduction.read.prepend_tidy_frame_with_tstep(places)
    place_change_events = generate_place_increased_events(places)
    transitions = read.read_tidy_csv(occ_test_files.files.RUN_90_TRANSITIONS, 'transition', drop_non_coloured_sums=True)
    transitions = occ.reduction.read.prepend_tidy_frame_with_tstep(transitions)
    transition_events = generate_transition_events(transitions)
    return graph_medium, place_change_events, transition_events

def _load_run_100():
    graph_medium = nx.read_gml(occ_test_files.files.RUN_100_GML, destringizer=int)
    places = read.read_tidy_csv(occ_test_files.files.RUN_100_PLACES, 'place', drop_non_coloured_sums=True)
    places = occ.reduction.read.prepend_tidy_frame_with_tstep(places)
    place_change_events = generate_place_increased_events(places)
    transitions = read.read_tidy_csv(occ_test_files.files.RUN_100_TRANSITIONS, 'transition', drop_non_coloured_sums=True)
    transitions = occ.reduction.read.prepend_tidy_frame_with_tstep(transitions)
    transition_events = generate_transition_events(transitions)
    return graph_medium, place_change_events, transition_events


def _load_run_77():
    graph_medium = _gen_loop_graph(6)
    places = read.read_tidy_csv(PLACES, 'place', drop_non_coloured_sums=True)
    places = occ.reduction.read.prepend_tidy_frame_with_tstep(places)
    place_change_events = generate_place_increased_events(places)
    transitions = read.read_tidy_csv(TRANSITIONS, 'transition', drop_non_coloured_sums=True)
    transitions = occ.reduction.read.prepend_tidy_frame_with_tstep(transitions)
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


