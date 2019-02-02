import os
import random
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from abc import ABC, abstractmethod
from typing import Sequence

import networkx as nx

from pyspike import petrinet


@dataclass(frozen=True)
class Color:
    name: str

    def place(self, name: str, initial_marking: str = '0`0', pos_offset: Sequence[int] = (0, 0)):
        return Place(self, name, initial_marking=initial_marking, pos_offset=pos_offset)

    def var(self, name: str):
        return Variable(self, name)


@dataclass(frozen=True)
class Variable:
    color: Color
    name: str


Unit = Color('Unit')
u = Unit.var('u')
n1 = Unit.var('n1')
n2 = Unit.var('n2')


class ColorFunction(ABC):
    """
    Assumed to return 'bool' until required otherwise.
    """

    def __init__(self, name, variable_list):
        self.name = name
        self.variables = variable_list

    def to_candl(self, medium_graph):
        sig = ','.join(f'{v.color.name} {v.name}' for v in self.variables)
        func = self._graph_to_func(medium_graph)
        return f'bool  {self.name}({sig}) {{ {func} }};'

    def __eq__(self, other):
        if type(self) != type(other):
            return False
        if self.name != other.name:
            return False
        return self.variables == other.variables

    @abstractmethod
    def _graph_to_func(self, medium_graph):
        pass


class IsNeighbour(ColorFunction):

    def __init__(self):
        super().__init__('is_neighbour', [u, n1])

    def _graph_to_func(self, medium_graph):
        return petrinet.graph_to_is_neighbour_func(
            medium_graph, unit_string=u.name, neighbour_sring=n1.name)


class AreBothNeighbours(ColorFunction):

    def __init__(self):
        super().__init__('are_both_neighbours', [u, n1, n2])

    def _graph_to_func(self, medium_graph):
        return petrinet.graph_to_are_both_neighbours_func(medium_graph)


# a_initial_toks = []
# b_initial_toks = []
# B_initial_toks = []
# A_initial_toks = []
#
# randomly_allocate_range_of_integers_between_lists((a_initial_toks, A_initial_toks), 30)
# randomly_allocate_range_of_integers_between_lists((b_initial_toks, b_initial_toks), 30)

NO_TOKENS_MARKING = "0`0"

def randomly_allocate_range_of_integers_between_lists(list_of_lists, number_nodes):
    for i in range(number_nodes):
        random.choice(list_of_lists).append(i)


def marking(list_of_nodes_indexes_with_one_token):
    if not list_of_nodes_indexes_with_one_token:
        return NO_TOKENS_MARKING
    else:
        return '++'.join(str(n) for n in list_of_nodes_indexes_with_one_token)

class Place:

    def __init__(self, color: Color, name: str, initial_marking: str = '0`0', pos_offset: Sequence[int] = (0, 0)):
        self.color = color
        self.name = name
        self.initial_marking = initial_marking
        self.pos_offset = tuple(pos_offset)

        assert isinstance(initial_marking, str)

        # TODO: Add a unicode name too if necessary

    def to_candl(self):
        return f'  {self.color.name} {self.name} = {self.initial_marking};'


class Transition(ABC):

    class Kind(Enum):
        STOCHASTIC = 1
        DETERMINISTIC = 2

    def __init__(self, source: Place, target: Place,
                 kind: Kind, transition_type_name: str, guard_function: ColorFunction = None, name_prefix=''):

        self.transition_type_name = transition_type_name
        self.source = source
        self.target = target
        self._kind = kind
        self.guard_function = guard_function
        self.name_prefix = name_prefix
        self. _validate_name_prefix()

    def _validate_name_prefix(self):
        # TODO: check only numbers and letters and no number st start (candl definition)
        if '_' in self.name_prefix:
            raise ValueError(f"Only number")

    def is_stochastic(self):
        return self._kind == Transition.Kind.STOCHASTIC

    def is_deterministic(self):
        return self._kind == Transition.Kind.DETERMINISTIC

    @property
    def name(self):
        return f"{self.name_prefix}{self.source.name}{self.target.name}"

    @staticmethod
    def expand_name(name):
        prefix = name[:-2]
        source = name[-2]
        target = name[-1]
        return prefix, source, target

    @abstractmethod
    def to_candl(self):
        pass


class FollowNeighbour(Transition):

    def __init__(self, source: Place, target: Place, rate: str = '1', name_prefix='',
                 use_read_arc=False, enabled_by_local: Place = None):  # TODO: consolidate enable/activate
        super().__init__(source, target,
                         Transition.Kind.STOCHASTIC, "follow_neighbour", IsNeighbour(),
                         name_prefix=name_prefix + ('f1L' if enabled_by_local else 'f1'))
        assert set(self.guard_function.variables) == {u, n1}
        self.rate = str(rate)
        assert not (use_read_arc and enabled_by_local)
        self.use_read_arc = use_read_arc
        self.enabled_by_local = enabled_by_local

    @property
    def name(self):
        ebl = self.enabled_by_local.name if self.enabled_by_local else ""
        return f"{self.name_prefix}{ebl}{self.source.name}{self.target.name}"

    def to_candl(self):
        s = self.source.name
        t = self.target.name

        if self.use_read_arc:
            return f"""\
  {self.name}
 {{[is_neighbour(u, n1)]}}
    : [{t} >= {{{n1.name}}}] & [{s} >= {{{u.name}}}]
    : [{t} + {{{u.name}}}]
    : {self.rate}
    ;"""

        elif self.enabled_by_local:
            e = self.enabled_by_local.name
            return f"""\
  {self.name}
 {{[is_neighbour(u, n1)]}}
    : [{t} >= {{{n1.name}}}] & [{e} >= {{{u.name}}}]
    : [{t} + {{{u.name}}}] & [{s} - {{{u.name}}}]
    : {self.rate}
    ;"""

        else:
            return f"""\
  {self.name}
 {{[is_neighbour(u, n1)]}}
    : [{t} >= {{{n1.name}}}]
    : [{t} + {{{u.name}}}] & [{s} - {{{u.name}}}]
    : {self.rate}
    ;"""


class FollowTwoNeighbours(Transition):

    def __init__(self, source: Place, target: Place, rate: str = '1', name_prefix='',
                 enabled_by_local: Place = None):
        super().__init__(source, target,
                         Transition.Kind.STOCHASTIC, "follow_two_neighbours", AreBothNeighbours(),
                         name_prefix=name_prefix + ('f2L' if enabled_by_local else 'f2'))
        assert set(self.guard_function.variables) == {u, n1, n2}
        self.rate = rate
        self.enabled_by_local = enabled_by_local

    @property
    def name(self):
        ebl = self.enabled_by_local.name if self.enabled_by_local else ""
        return f"{self.name_prefix}{ebl}{self.source.name}{self.target.name}"

    def to_candl(self):
        s = self.source.name
        t = self.target.name
        if self.enabled_by_local:
            e = self.enabled_by_local.name
            return f'''\
  {self.name}
 {{[are_both_neighbours(u, n1, n2)]}}
    : [{t} >= {{n1++n2}}] & [{e} >= {{{u.name}}}]
    : [{t} + {{u}}] & [{s} - {{u}}]
    : {self.rate}
    ;'''
        else:  # not enabled_by_local
            return f'''\
  {self.name}
 {{[are_both_neighbours(u, n1, n2)]}}
    : [{t} >= {{n1++n2}}]
    : [{t} + {{u}}] & [{s} - {{u}}]
    : {self.rate}
    ;'''


class ModulatedInternal(Transition):

    def __init__(self, source: Place, target: Place, activate: Place, activate2: Place = None,
                 rate: str = '1', name_prefix=''):
        super().__init__(source, target,
                         Transition.Kind.STOCHASTIC, "modulated_internal", AreBothNeighbours(),
                         name_prefix=name_prefix + 'mi2' if activate2 else 'mi')
        assert set(self.guard_function.variables) == {u, n1, n2}
        self.activate = activate
        self.activate2 = activate2
        self.rate = rate

    @property
    def name(self):
        ebl = self.activate.name if self.activate else ""
        ebl2 = self.activate2.name if self.activate2 else ""
        return f"{self.name_prefix}{ebl}{ebl2}{self.source.name}{self.target.name}"

    def to_candl(self):
        s = self.source.name
        t = self.target.name
        m = self.activate.name
        if self.activate2:
            m2 = self.activate2.name
            activate2_term = f" & [{m2} >= {{u}}]"
        else:
            activate2_term = ""
        return f'''\
  {self.name}
    : [{m} >= {{u}}]{activate2_term}
    : [{t} + {{u}}] & [{s} - {{u}}]
    : {self.rate}
    ;'''



class External(Transition):

    def __init__(self, source: Place, target: Place, delay_time: float, unit_list, name_prefix=''):
        super().__init__(source, target,
                         Transition.Kind.DETERMINISTIC, "external_message", name_prefix=name_prefix + 'ext')
        self.unit_list = unit_list
        self.delay_time = float(delay_time)

    def to_candl(self):
        s = self.source.name
        t = self.target.name
        markings = '++'.join((str(i) for i in self.unit_list))
        return f"""\
  {self.name}
    :
    : [{t} + {{{markings}}}] & [{s} - {{{markings}}}]
    : {self.delay_time}
    ;"""


class UnitModel:
    """
    Colorset of Unit only for now.
    """
    def __init__(self, name: str,
                 colors: Sequence[Color],
                 variables: Sequence[Variable],
                 places: Sequence[Place] = (),
                 transitions: Sequence[Transition] = ()):
        self.name = name
        self.colors = colors
        self.variables = variables

        self.places = []
        self.transitions = []
        self.functions = []

        self.add_places_from(places)
        self.add_transitions_from(transitions)

    def add_places_from(self, place_list):
        for place in place_list:
            self.add_place(place)

    def add_transitions_from(self, transition_list):
        for t in transition_list:
            self.add_transition(t)

    def add_place(self, place):
        if place.color not in self.colors:
            raise ValueError(f"Color '{place.color.name}' not in this model")
        self.places.append(place)

    def add_transition(self, transition):
        t = transition
        if t.source not in self.places:
            self.add_place(t.source)
        if t.target not in self.places:
            self.add_place(t.target)
        if (t.guard_function is not None) and (t.guard_function not in self.functions):
            self._add_function(t.guard_function)
        if t.name in [tt.name for tt in self.transitions]:
            raise ValueError(f"There is already a transition names '{t.name}'")
        self.transitions.append(t)

    def to_candl_string(self, graph_medium: nx.Graph, graph_name='') -> str:
        chunks = [
            self._title_chunk(graph_name) + '\n{',
            self._colorsets_chunk(graph_medium),
            self._variables_chunk(),
            self._colorfunctions_chunk(graph_medium),
            self._places_chunk(),
            self._transitions_chunk(),
            '}'
        ]
        return '\n'.join(chunks) + '\n'

    def to_candl_file(self, graph_medium: nx.Graph, graph_name, dir_path) -> Path:
        """Create .candl file by embeding this UnitModel onto a graph described by graph_medium.
        Return a Path to the created file.

        """
        candl_string = self.to_candl_string(graph_medium, graph_name)
        file_name = self._full_name(graph_name) + '.candl'
        file_name = file_name.replace(' ', '-')
        file_path = os.path.join(dir_path, file_name)
        with open(file_path, 'w') as f:
            f.write(candl_string)
        return Path(file_path)

    def _full_name(self, graph_name):
        return self.name + ' on ' + graph_name

    # def to_bipartite_graph(self):
    #     assert False

    def _add_function(self, function: ColorFunction):
        f = function
        assert f not in self.functions
        # if f.guard_function:  # TODO: turn inside out: instead ask function if it is okay with self.variables
        for v in f.variables:
            if v not in self.variables:
                raise ValueError(f"Variable '{v.name}' required by function '{f.name}' not in this model")
        self.functions.append(f)

    def _title_chunk(self, graph_name=None):
        name = self._full_name(graph_name) if graph_name else self.name
        return f'colspn  [{name}]'

    def _colorsets_chunk(self, graph_medium: nx.Graph):
        # colorsets:
        #   Unit = {$RANGE$};
        lines = ['colorsets:']
        for c in self.colors:
            assert c.name == 'Unit', 'Only know about Unit so far'
            # NOTE: If expanding to support other types then this logic should be pushed down into Color
            lines.append(f"  {c.name} = {{0..{graph_medium.number_of_nodes()-1}}};")
        # lines.append()
        return '\n'.join(lines) + '\n'

    def _variables_chunk(self):
        lines = ['variables:']
        for v in self.variables:
            lines.append(f'  {v.color.name} : {v.name};')
        return '\n'.join(lines) + '\n'

    def _colorfunctions_chunk(self, graph_medium):
        lines = ['colorfunctions:']
        for f in self.functions:
            lines.append(f.to_candl(graph_medium))
        return '\n'.join(lines) + '\n'

    def _places_chunk(self):
        lines = ['places:',
                 'discrete:']
        for p in self.places:
            lines.append(f'  {p.color.name} {p.name} = {p.initial_marking};')
        return '\n'.join(lines) + '\n'

    def _transitions_chunk(self):

        stochastic_candle_bits = []
        deterministic_candle_bits = []

        for t in self.transitions:
            if t.is_stochastic():
                stochastic_candle_bits.append(t.to_candl())
            if t.is_deterministic():
                deterministic_candle_bits.append(t.to_candl())

        bits = ['transitions:']
        bits.extend(stochastic_candle_bits)
        if deterministic_candle_bits:
            bits.append('deterministic:')
            bits.extend(deterministic_candle_bits)

        return '\n'.join(bits) + '\n'


    # def update(self):
    #
    #     # see nx.Graph().update()
    #     pass




