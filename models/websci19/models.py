# %% Setup

from occ.model import FollowNeighbour as follow1
from pyspike.model import UnitModel, u, n1, n2, Unit, randomly_allocate_range_of_integers_between_lists, marking


def generate_pair_with_random_markings(name1, name2, num_nodes, pos_offset=(0, 0)):
    initial1 = []
    initial2 = []
    randomly_allocate_range_of_integers_between_lists((initial1, initial2), num_nodes)
    place1 = Unit.place(name1, marking(initial1), pos_offset=pos_offset)
    place2 = Unit.place(name2, marking(initial2), pos_offset=pos_offset)
    return place1, place2

def generate_pair_with_marking(name1, name2, num_nodes, place_1_index_list, pos_offset=(0, 0)):
    place_2_index_list = list(range(num_nodes))
    for i in place_1_index_list:
        place_2_index_list.remove(i)
    place1 = Unit.place(name1, marking(place_1_index_list), pos_offset=pos_offset)
    place2 = Unit.place(name2, marking(place_2_index_list), pos_offset=pos_offset)
    return place1, place2


def generate_single_pair_aA_with_random_marking(num_nodes):
    a, A = generate_pair_with_random_markings('a', 'A', num_nodes)

    m = UnitModel(name="random single pair ", colors=[Unit], variables=[u, n1, n2], places=[a, A])

    m.add_transitions_from([
        follow1(a, A),
        follow1(A, a),
    ])

    return m



# def generate_non_conflated_unit(num_nodes):
#
#     a, A, b, B, e, E = generate_aAbBeE_pairs_with_random_markings(num_nodes)
#
#     m = UnitModel(name="aA and bB non conflated", colors=[Unit], variables=[u, n1, n2], places=[a, A, b, B])
#
#     m.add_transitions_from([
#         follow1(a, A),
#         follow1(A, a),
#         follow1(b, B),
#         follow1(B, b),
#     ])
#
#     return m




