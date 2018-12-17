import os
from pathlib import Path

import networkx as nx

from pyspike.sacred import call
from pyspike.sacred.call import run_experiment

from pyspike.model import UnitModel, u, n1, n2, Unit
from pyspike.model import FollowNeighbour as follow1
from pyspike.model import FollowTwoNeighbours as follow2
from pyspike.model import External as ext

PATH = Path(__file__)

a = Unit.place('a', '1`all')
b = Unit.place('b')
c = Unit.place('c')
C = Unit.place('C')

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

medium_graph = nx.Graph([(0, 1), (1, 2), (2, 0), (2, 3)])


def test_Call():
    call.run_experiment(m, medium_graph, graph_name='four graph', calling_file=PATH, file_storage_observer=True)

