import networkx as nx
from sacred import Ingredient

import pyspike
import occ.vis.occasion_graph
import occ.vis.network
from pathlib import Path

from pyspike import tidydata

visualisation_ingredient = Ingredient('visualisation')


@visualisation_ingredient.config
def visualisation_config():
    medium_gml_path = False
    num_runs = 1


@visualisation_ingredient.capture
def visualise_temporal_graph(places_path: Path, transitions_path: Path, medium_gml_path: Path, run_id=None):
    assert places_path.exists()
    assert transitions_path.exists()
    assert medium_gml_path.exists()

    places = tidydata.read_csv(filename=str(places_path), node_type="place", drop_non_coloured_sums=True)
    transitions = tidydata.read_csv(filename=str(transitions_path), node_type="transition", drop_non_coloured_sums=True)
    _, _, tstep = tidydata.determine_time_range_of_data_frame(places)
    places = pyspike.tidydata.prepend_tidy_frame_with_tstep(places)
    transitions = pyspike.tidydata.prepend_tidy_frame_with_tstep(transitions)

    place_change_events = occ.vis.occasion_graph.generate_place_increased_events(places)
    transition_events = occ.vis.occasion_graph.generate_transition_events(transitions)

    causal_graph = occ.vis.occasion_graph.generate_causal_graph(
        place_change_events, transition_events, time_per_step=tstep)
    print('str(medium_gml_path): ' + str(medium_gml_path))
    medium_graph = nx.read_gml(str(medium_gml_path), destringizer=int)

    fig = occ.vis.occasion_graph.generate_causal_graph_figure(causal_graph, medium_graph, run_id=run_id)
    return fig
    # plot_url = py.iplot(fig, filename='causal_graph.html')
    # return plot_url


@visualisation_ingredient.capture
def visualise_network_animation(places_path: Path, medium_gml_path: Path, num_runs: int, run_id=None):
    assert places_path.exists()
    assert medium_gml_path.exists()

    places = tidydata.read_csv(filename=str(places_path), node_type="place", drop_non_coloured_sums=True)
    places = pyspike.tidydata.prepend_tidy_frame_with_tstep(places)
    medium_graph = nx.read_gml(str(medium_gml_path), destringizer=int)

    fig = occ.vis.network.generate_network_animation_figure_with_slider(
        places, medium_graph, run_id=run_id, num_runs=num_runs)
    return fig
    # plot_url = py.plot(fig,  filename='network_animation_with_slider.html')
    # return plot_url
