from dataclasses import dataclass

import networkx as nx

from pyspike.model import UnitModel, u, n1, n2, Unit, Place, Transition, Color, marking
from pyspike.exe import SimArgs

from occ.model.transitions import FollowNeighbour as follow1
from occ.model.transitions import FollowTwoNeighbours as follow2
from occ.model.transitions import External as ext


__all__ = ['u', 'n1', 'n2', 'Unit', 'UnitModel', 'follow1', 'follow2', 'ext', 'Place', 'Transition', 'SimArgs',
           'SystemModel', 'Color', 'marking']


@dataclass(frozen=True)
class SystemModel:
    unit: UnitModel
    network: nx.Graph  # multiple later. depends on unit
    network_name: str  # TODO: move onto nx.Graph attribute
    marking: dict = None
