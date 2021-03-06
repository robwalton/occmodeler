import os
import random
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from abc import ABC, abstractmethod
from typing import Sequence

import networkx as nx


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
        name = name.replace(' ', '_')
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




