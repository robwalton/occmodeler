import pytest

import networkx as nx

from pyspike import model
from pyspike.model import ColorFunction

# import occ.model


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


class TestFunctions:

    class MockColorFunction(ColorFunction):

        def _graph_to_func(self):
            return "something"

    def test_equality(self):
        mcf_1 = TestFunctions.MockColorFunction('one', [model.n1])
        mcf_2 = TestFunctions.MockColorFunction('two', [model.n2])
        assert mcf_1 == mcf_1
        assert mcf_2 == mcf_2
        assert mcf_1 in [mcf_1]
        assert mcf_2 != mcf_1


def test_place_to_candl():
    p = model.Place(model.Unit, 'a', '1`all')
    assert p.to_candl() == '  Unit a = 1`all;'


class TestTransitions:

    class MockTransition(model.Transition):
        def to_candl(self):
            return "something"

    def test_expand_name(self):
        assert TestTransitions.MockTransition.expand_name('prefixab') == ('prefix', 'a', 'b')

    def test_transition_with_underscores_in_prefix_fails(self, place_a, place_b):
        with pytest.raises(ValueError):
            TestTransitions.MockTransition(place_a, place_b, model.Transition.Kind.STOCHASTIC, 'name', name_prefix='with_underscore')


class MockFunction2(ColorFunction):  # based on AreBothNeighbours

    def __init__(self):
        super().__init__('mock_func_2', [model.u, model.n1, model.n2])

    def _graph_to_func(self, medium_graph):
        return "something"


class MockFunction1(ColorFunction):  # based on IsNneighbour

    def __init__(self):
        super().__init__('mock_func_1', [model.u, model.n1])

    def _graph_to_func(self, medium_graph):
        return "something"


class TestUnitModel:

    def test_add_place(self, m, place_a):
        m.add_place(place_a)
        assert m.places == [place_a]

    def test_add_place_with_missing_color(self, m):
        with pytest.raises(ValueError):
            m.add_place(model.Place(model.Color('new'), 'n', ''))

    def test__add_function_with_missing_variable(self, m, place_a, place_b):
        with pytest.raises(ValueError):
            m._add_function(MockFunction2())

    # TODO: many tests moved to occ/tests/test_model for speed. Move back here




