import pytest

import networkx as nx

from occ import model


@pytest.fixture()
def medium_graph():
    return nx.Graph([(1, 2), (2, 3), (3, 1), (3, 4)])


@pytest.fixture()
def place_a():
    return model.Place(model.Unit, 'a', '1`all')


@pytest.fixture()
def place_b():
    return model.Place(model.Unit, 'b', '0`0')


@pytest.fixture()
def place_e():
    return model.Place(model.Unit, 'e', '0`0')


@pytest.fixture()
def m():
    return model.UnitModel(
        'some name',
        [model.Unit],
        [model.u, model.n1]
        # leave out n2 required for FollowTwoNeighbours
    )


IS_NEIGHBOUR_CANDL = (
    'bool  is_neighbour(Unit u,Unit n1) '
    '{ (u=1 & (n1=2|n1=3)) | (u=2 & (n1=1|n1=3)) | (u=3 & (n1=1|n1=2|n1=4)) | (u=4 & (n1=3)) };')

ARE_BOTH_NEIGHBOURS_CANDLE = (
    'bool  are_both_neighbours(Unit u,Unit n1,Unit n2) '
    '{ (n1!=n2) & ((u=1 & (n1=2|n1=3) & (n2=2|n2=3)) | (u=2 & (n1=1|n1=3) & '
    '(n2=1|n2=3)) | (u=3 & (n1=1|n1=2|n1=4) & (n2=1|n2=2|n2=4)) | (u=4 & (n1=3) & (n2=3))) };')


class TestFunctions:

    def test_is_neighbour_candl(self, medium_graph):
        f = model.IsNeighbour()
        assert f.to_candl(medium_graph) == IS_NEIGHBOUR_CANDL

    def test_are_both_neighbours_candl(self, medium_graph):
        f = model.AreBothNeighbours()
        assert f.to_candl(medium_graph) == ARE_BOTH_NEIGHBOURS_CANDLE


class TestTransitions:

    def test_follow_neighbour_to_candl_with_mass_action(self, place_a, place_b):
        t = model.FollowNeighbour(place_a, place_b, rate='MassAction(1)')
        assert t.to_candl() == """\
  f1ab
 {[is_neighbour(u, n1)]}
    : [b >= {n1}]
    : [b + {u}] & [a - {u}]
    : MassAction(1)
    ;"""

    def test_follow_neighbour_to_candl_with_rate_1(self, place_a, place_b):
        t = model.FollowNeighbour(place_a, place_b)
        assert t.to_candl() == """\
  f1ab
 {[is_neighbour(u, n1)]}
    : [b >= {n1}]
    : [b + {u}] & [a - {u}]
    : 1
    ;"""

    def test_follow_neighbour_to_candl_with_rate_1_enabled_by_local(self, place_a, place_b):
        place_e = model.Place(model.Unit, 'e')
        t = model.FollowNeighbour(place_a, place_b, enabled_by_local=place_e)
        assert t.to_candl() == """\
  f1Leab
 {[is_neighbour(u, n1)]}
    : [b >= {n1}] & [e >= {u}]
    : [b + {u}] & [a - {u}]
    : 1
    ;"""

    def test_follow_neighbour_to_candl_with_rate_1_use_read_arc(self, place_a, place_b):
        t = model.FollowNeighbour(place_a, place_b, use_read_arc=True)
        assert t.to_candl() == """\
  f1ab
 {[is_neighbour(u, n1)]}
    : [b >= {n1}] & [a >= {u}]
    : [b + {u}]
    : 1
    ;"""

    def test_follow_neighbour_to_candl_with_rate_name_prefix(self, place_a, place_b):
        t = model.FollowNeighbour(place_a, place_b, name_prefix='xyz')
        assert t.to_candl() == """\
  xyzf1ab
 {[is_neighbour(u, n1)]}
    : [b >= {n1}]
    : [b + {u}] & [a - {u}]
    : 1
    ;"""

    def test_follow_two_neighbours_to_candl(self, place_a, place_b):
        t = model.FollowTwoNeighbours(place_a, place_b)
        assert t.to_candl() == """\
  f2ab
 {[are_both_neighbours(u, n1, n2)]}
    : [b >= {n1++n2}]
    : [b + {u}] & [a - {u}]
    : 1
    ;"""

    def test_follow_two_neighbours_to_candl_with_rate_1_enabled_by_local(self, place_a, place_b):
        place_e = model.Place(model.Unit, 'e')
        t = model.FollowTwoNeighbours(place_a, place_b, enabled_by_local=place_e)
        assert t.to_candl() == """\
  f2Leab
 {[are_both_neighbours(u, n1, n2)]}
    : [b >= {n1++n2}] & [e >= {u}]
    : [b + {u}] & [a - {u}]
    : 1
    ;"""

    def test_modulated_internal(self, place_a, place_b, place_e):
        t = model.ModulatedInternal(place_a, place_b, place_e)
        assert t.to_candl() == """\
  mieab
    : [e >= {u}]
    : [b + {u}] & [a - {u}]
    : 1
    ;"""

    def test_modulated_internal_with_two(self, place_a, place_b, place_e):
        place_f = model.Place(model.Unit, 'f', '0`0')
        t = model.ModulatedInternal(place_a, place_b, place_e, activate2=place_f)
        assert t.to_candl() == """\
  mi2efab
    : [e >= {u}] & [f >= {u}]
    : [b + {u}] & [a - {u}]
    : 1
    ;"""

    def test_external_to_candl(self, place_a, place_b):
        t = model.External(place_a, place_b, 2, [15, 16])
        assert t.to_candl() == """\
  extab
    :
    : [b + {15++16}] & [a - {15++16}]
    : 2.0
    ;"""


def test_integration(medium_graph):

    from pyspike.model import UnitModel, u, n1, n2, Place, Unit
    from occ.model import FollowNeighbour as follow1
    from occ.model import FollowTwoNeighbours as follow2
    from occ.model import External as ext

    m = UnitModel(
        name='last_registered_two_neighbours_required',
        colors=[Unit],
        variables=[u, n1, n2])

    a = Unit.place('a', '1`all')
    b = Unit.place('b')
    c = Unit.place('c')
    C = Unit.place('C')

    m.add_places_from([a, b, c, C])

    m.add_transitions_from([
        follow1(a, b),
        follow2(b, c),
        follow2(b, C),
        follow2(c, C),
        follow2(C, c),
        ext(a, b, 1, [0, 15]),
        ext(b, C, 2, [15, 16]),
        ext(b, c, 2, [0, 29]),
    ])
    print('---')
    print(m.to_candl_string(medium_graph))
    print('---')
    assert m.to_candl_string(medium_graph) == """\
colspn  [last_registered_two_neighbours_required]
{
colorsets:
  Unit = {0..3};

variables:
  Unit : u;
  Unit : n1;
  Unit : n2;

colorfunctions:
bool  is_neighbour(Unit u,Unit n1) { (u=1 & (n1=2|n1=3)) | (u=2 & (n1=1|n1=3)) | (u=3 & (n1=1|n1=2|n1=4)) | (u=4 & (n1=3)) };
bool  are_both_neighbours(Unit u,Unit n1,Unit n2) { (n1!=n2) & ((u=1 & (n1=2|n1=3) & (n2=2|n2=3)) | (u=2 & (n1=1|n1=3) & (n2=1|n2=3)) | (u=3 & (n1=1|n1=2|n1=4) & (n2=1|n2=2|n2=4)) | (u=4 & (n1=3) & (n2=3))) };

places:
discrete:
  Unit a = 1`all;
  Unit b = 0`0;
  Unit c = 0`0;
  Unit C = 0`0;

transitions:
  f1ab
 {[is_neighbour(u, n1)]}
    : [b >= {n1}]
    : [b + {u}] & [a - {u}]
    : 1
    ;
  f2bc
 {[are_both_neighbours(u, n1, n2)]}
    : [c >= {n1++n2}]
    : [c + {u}] & [b - {u}]
    : 1
    ;
  f2bC
 {[are_both_neighbours(u, n1, n2)]}
    : [C >= {n1++n2}]
    : [C + {u}] & [b - {u}]
    : 1
    ;
  f2cC
 {[are_both_neighbours(u, n1, n2)]}
    : [C >= {n1++n2}]
    : [C + {u}] & [c - {u}]
    : 1
    ;
  f2Cc
 {[are_both_neighbours(u, n1, n2)]}
    : [c >= {n1++n2}]
    : [c + {u}] & [C - {u}]
    : 1
    ;
deterministic:
  extab
    :
    : [b + {0++15}] & [a - {0++15}]
    : 1.0
    ;
  extbC
    :
    : [C + {15++16}] & [b - {15++16}]
    : 2.0
    ;
  extbc
    :
    : [c + {0++29}] & [b - {0++29}]
    : 2.0
    ;

}
"""

class TestUnitModel:

    # TODO: many tests here should be moved to pyspike/tests/test_model.py
    def test_add_transition_with_new_places(self, m, place_a, place_b):
        t = model.External(place_a, place_b, 1, [10, 15])
        m.add_transition(t)
        assert m.places == [place_a, place_b]
        assert m.functions == []  # model.External has no guard function
        assert m.transitions == [t]

    def test_add_transition_with_new_function(self, m, place_a, place_b):
        m.variables.append(model.n2)
        m.add_places_from([place_a, place_b])
        t = model.FollowTwoNeighbours(place_a, place_b)
        m.add_transition(t)
        assert m.places == [place_a, place_b]
        assert m.transitions == [t]
        print('t.guard_function:', t.guard_function)
        assert m.functions == [model.AreBothNeighbours()]

    def test_add_transition_with_duplicate_name_fails(self, m, place_a, place_b):
        m.variables.append(model.n2)
        m.add_places_from([place_a, place_b])
        t = model.FollowTwoNeighbours(place_a, place_b)
        m.add_transition(t)
        with pytest.raises(ValueError):
            m.add_transition(t)

    def test__colorsets_chunk(self, m, medium_graph):
        assert m._colorsets_chunk(medium_graph) == """\
colorsets:
  Unit = {0..3};
"""

    def test__variables_chunk(self, m):
        assert m._variables_chunk() == """\
variables:
  Unit : u;
  Unit : n1;
"""

    def test__colorfunctions_chunk(self, m, medium_graph):
        m.functions = [model.IsNeighbour()]
        assert m._colorfunctions_chunk(medium_graph) == (
                'colorfunctions:\n' + IS_NEIGHBOUR_CANDL + '\n')

    def test__places_chunk(self, m, place_a, place_b):
        m.add_places_from([place_a, place_b])
        assert m._places_chunk() == """\
places:
discrete:
  Unit a = 1`all;
  Unit b = 0`0;
"""

    def test__transitions_chunk(self, m, place_a, place_b):
        m.transitions = [model.FollowNeighbour(place_a, place_b),
                         model.External(place_a, place_b, 2, [15, 16])]
        assert m._transitions_chunk() == """\
transitions:
  f1ab
 {[is_neighbour(u, n1)]}
    : [b >= {n1}]
    : [b + {u}] & [a - {u}]
    : 1
    ;
deterministic:
  extab
    :
    : [b + {15++16}] & [a - {15++16}]
    : 2.0
    ;
"""
