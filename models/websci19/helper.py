import os
import pathlib
import sys

import networkx as nx
from pyspike.model import Unit, randomly_allocate_range_of_integers_between_lists, marking


def bodge_path():
    for package in ['occ', 'pyspike', 'occdash']:
        _add_to_path_if_necessary(package)


def _add_to_path_if_necessary(package: str):
    package_dir = str(pathlib.Path(os.path.abspath('')).parents[1] / package)
    if package_dir not in sys.path:
        sys.path.insert(0, package_dir)
    #     print(f"Added to python path: '{package_dir}'")
    # else:
    #     print(f"'{package}' already on python path!")


def sym_bar_like_network(nodes_per_half=7, seed_a=1, seed_b=2):
    """Symmetrical bar bell like network"""
    a = nx.newman_watts_strogatz_graph(nodes_per_half, 4, 0.1, seed=seed_a)
    b = nx.newman_watts_strogatz_graph(nodes_per_half, 4, 0.1, seed=seed_b)
    G = nx.compose(a, nx.convert_node_labels_to_integers(b, first_label=nodes_per_half))
    G.add_edge(nodes_per_half - 1, nodes_per_half);
    # nx.draw_kamada_kawai(G)
    # plt.show()
    return G


def two_community_network():
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


def generate_place_pair_with_random_markings(name1, name2, num_nodes, pos_offset=(0, 0)):
    initial1 = []
    initial2 = []
    randomly_allocate_range_of_integers_between_lists((initial1, initial2), num_nodes)
    place1 = Unit.place(name1, marking(initial1), pos_offset=pos_offset)
    place2 = Unit.place(name2, marking(initial2), pos_offset=pos_offset)
    return place1, place2


def generate_place_pair_with_marking(name1, name2, num_nodes, place_1_index_list, pos_offset=(0, 0)):
    place_2_index_list = list(range(num_nodes))
    for i in place_1_index_list:
        place_2_index_list.remove(i)
    place1 = Unit.place(name1, marking(place_1_index_list), pos_offset=pos_offset)
    place2 = Unit.place(name2, marking(place_2_index_list), pos_offset=pos_offset)
    return place1, place2
