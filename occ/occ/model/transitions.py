from occ.model.colour_functions import IsNeighbour, AreBothNeighbours
from pyspike.model import Transition, Place, u, n1, n2


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