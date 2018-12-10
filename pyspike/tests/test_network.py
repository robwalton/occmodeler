import networkx as nx
import plotly.offline as py

from pyspike import read_csv, tidydata
from pyspike.network import generate_network_animation_figure_with_slider
from tests.files import RUN_71_PLACES, RUN_71_TRANSITIONS, RUN_71_NETWORK_GML


PLOT = True


def test_generate_network_animation_figure_with_slider():

    places = read_csv(RUN_71_PLACES, 'place', drop_non_coloured_sums=True)
    places = tidydata.prepend_tidy_frame_with_tstep(places)
    # transitions = read_csv(RUN_71_TRANSITIONS, 'transition', drop_non_coloured_sums=True)
    # transitions = tidydata.prepend_tidy_frame_with_tstep(transitions)

    medium_graph = nx.read_gml(RUN_71_NETWORK_GML, destringizer=int)
    medium_layout = nx.spring_layout(medium_graph, dim=2)

    fig = generate_network_animation_figure_with_slider(places, medium_graph, medium_layout)
    if PLOT:
        py.plot(fig)

