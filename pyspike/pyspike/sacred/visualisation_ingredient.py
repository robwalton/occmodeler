import os

import networkx as nx
from sacred import Ingredient

import pyspike
import pyspike.temporal
import pyspike.network
from pathlib import Path
import plotly.offline as py

from pyspike import tidydata

visualisation_ingredient = Ingredient('visualisation')


@visualisation_ingredient.config
def visualisation_config():
    enable = True
    jupyter_inline = False
    medium_gml_path = False


@visualisation_ingredient.capture
def visualise_temporal_graph(places_path: Path, transitions_path: Path, medium_gml_path: Path, jupyter_inline, enable: bool, run_id=None):
    assert places_path.exists()
    assert transitions_path.exists()
    assert medium_gml_path.exists()

    places = tidydata.read_csv(filename=str(places_path), node_type="place", drop_non_coloured_sums=True)
    transitions = tidydata.read_csv(filename=str(transitions_path), node_type="transition", drop_non_coloured_sums=True)
    _, _, tstep = tidydata.determine_time_range_of_data_frame(places)
    places = pyspike.tidydata.prepend_tidy_frame_with_tstep(places)
    transitions = pyspike.tidydata.prepend_tidy_frame_with_tstep(transitions)

    place_change_events = pyspike.temporal.generate_place_change_events(places)
    transition_events = pyspike.temporal.generate_transition_events(transitions)

    causal_graph = pyspike.temporal.generate_causal_graph(
        place_change_events, transition_events, time_per_step=tstep)
    print('str(medium_gml_path): ' + str(medium_gml_path))
    medium_graph = nx.read_gml(str(medium_gml_path), destringizer=int)

    fig = pyspike.temporal.generate_causal_graph_figure(causal_graph, medium_graph, run_id=run_id)
    return fig
    # plot_url = py.iplot(fig, filename='causal_graph.html')
    # return plot_url


@visualisation_ingredient.capture
def visualise_network_animation(places_path: Path, medium_gml_path: Path, jupyter_inline, enable: bool, run_id=None):
    assert places_path.exists()
    assert medium_gml_path.exists()

    places = tidydata.read_csv(filename=str(places_path), node_type="place", drop_non_coloured_sums=True)
    places = pyspike.tidydata.prepend_tidy_frame_with_tstep(places)
    medium_graph = nx.read_gml(str(medium_gml_path), destringizer=int)

    fig = pyspike.network.generate_network_animation_figure_with_slider(places, medium_graph, run_id=run_id)
    return fig
    # plot_url = py.plot(fig,  filename='network_animation_with_slider.html')
    # return plot_url
