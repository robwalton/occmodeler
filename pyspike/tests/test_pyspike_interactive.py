import os
from pathlib import Path

import networkx as nx
import pytest

from pyspike.sacred import call
from pyspike.sacred.call import run_experiment

from pyspike.model import UnitModel, u, n1, n2, Unit
from pyspike.model import FollowNeighbour as follow1
from pyspike.model import FollowTwoNeighbours as follow2
from pyspike.model import External as ext

PATH = Path(__file__)

@pytest.fixture
def a():
    return Unit.place('a', '1`all')

@pytest.fixture
def b():
    return Unit.place('b')

@pytest.fixture
def c():
    return Unit.place('c')

@pytest.fixture
def C():
    return Unit.place('C')


@pytest.fixture
def m(a, b, c, C):
    m = UnitModel(
        name='last_registered_two_neighbours_required',
        colors=[Unit],
        variables=[u, n1, n2],
        places=[a, b, c, C]
    )

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
    return m

@pytest.fixture
def medium_graph():
    return nx.Graph([(0, 1), (1, 2), (2, 0), (2, 3)])

def test_places(a, b, c, C):
    assert a.to_candl() == '  Unit a = 1`all;'
    assert b.to_candl() == '  Unit b = 0`0;'
    assert c.to_candl() == '  Unit c = 0`0;'
    assert C.to_candl() == '  Unit C = 0`0;'
    assert a.name == 'a'


def test_Call(m, medium_graph):
    call.run_experiment(m, medium_graph, graph_name='four graph', calling_file=PATH, file_storage_observer=True)

