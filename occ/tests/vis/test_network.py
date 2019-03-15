import networkx as nx
import plotly.offline as py

from pyspike.tidydata import read_csv
from pyspike import tidydata
from occ.vis.network import generate_network_animation_figure_with_slider
from occ_test_files import RUN_71_PLACES, RUN_71_NETWORK_GML, MONTE_CARLO_TOS_10000


PLOT = True


def test_generate_network_animation_figure_with_slider():

    places = read_csv(RUN_71_PLACES, 'place', drop_non_coloured_sums=True)
    places = tidydata.prepend_tidy_frame_with_tstep(places)
    places.query('time < 8', inplace=True)

    medium_graph = nx.read_gml(RUN_71_NETWORK_GML, destringizer=int)
    medium_layout = nx.spring_layout(medium_graph, dim=2)

    fig = generate_network_animation_figure_with_slider(places, medium_graph, medium_layout)
    if PLOT:
        py.plot(fig)


def test_generate_network_animation_figure_with_slider_with_monte_carlo():

    places = read_csv(MONTE_CARLO_TOS_10000, 'place', drop_non_coloured_sums=True)
    places = tidydata.prepend_tidy_frame_with_tstep(places)
    places.query('time < 3', inplace=True)

    medium_graph = nx.read_gml(RUN_71_NETWORK_GML, destringizer=int)
    medium_layout = nx.spring_layout(medium_graph, dim=2)

    fig = generate_network_animation_figure_with_slider(places, medium_graph, medium_layout)
    if PLOT:
        py.plot(fig)

