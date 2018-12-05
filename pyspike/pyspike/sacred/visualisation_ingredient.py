import os

import networkx as nx
from sacred import Ingredient

import pyspike
import pyspike.temporal
from pathlib import Path
import plotly.offline as py


visualisation_ingredient = Ingredient('visualisation')


@visualisation_ingredient.config
def visualisation_config():
    enable = True


@visualisation_ingredient.capture
def visualise_temporal_graph(places_path: Path, transitions_path: Path, medium_gml_path: Path, enable: bool):
    assert places_path.exists()
    assert transitions_path.exists()
    assert medium_gml_path.exists()

    places = pyspike.read_csv(filename=str(places_path), node_type="place", drop_non_coloured_sums=True)
    transitions = pyspike.read_csv(filename=str(transitions_path), node_type="transition", drop_non_coloured_sums=True)

    places = pyspike.tidydata.prepend_tidy_frame_with_tstep(places)
    transitions = pyspike.tidydata.prepend_tidy_frame_with_tstep(transitions)

    place_change_events = pyspike.temporal.generate_place_change_events(places)
    transition_events = pyspike.temporal.generate_transition_events(transitions)

    causal_graph = pyspike.temporal.generate_causal_graph(
        place_change_events, transition_events)

    medium_graph = nx.read_gml(str(medium_gml_path), destringizer=int)

    fig = pyspike.temporal.generate_causal_graph_figure(causal_graph, medium_graph)
    plot_url = py.plot(fig)
    return plot_url
