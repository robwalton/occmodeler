from pyspike.model import ColorFunction, u, n1, n2


class IsNeighbour(ColorFunction):

    def __init__(self):
        super().__init__('is_neighbour', [u, n1])

    def _graph_to_func(self, medium_graph):
        return graph_to_is_neighbour_func(
            medium_graph, unit_string=u.name, neighbour_sring=n1.name)


class AreBothNeighbours(ColorFunction):

    def __init__(self):
        super().__init__('are_both_neighbours', [u, n1, n2])

    def _graph_to_func(self, medium_graph):
        return graph_to_are_both_neighbours_func(medium_graph)


def graph_to_is_neighbour_func(g, unit_string='x', neighbour_sring='y'):

    x_list = []

    for x in sorted(g.adj.keys()):
        y_list = []
        for y in sorted(g.adj[x].keys()):
            y_list.append(f'{neighbour_sring}={y}')
        if y_list:
            x_list.append(f"({unit_string}={x} & ({'|'.join(y_list)}))")

    return ' | '.join(x_list)


def graph_to_are_both_neighbours_func(g):

    u_list = []

    for u in sorted(g.adj.keys()):
        n1_list = []
        n2_list = []
        for y in sorted(g.adj[u].keys()):
            n1_list.append(f'n1={y}')
            n2_list.append(f'n2={y}')
        if n1_list:  # and implicitly n2_list
            u_list.append(f"(u={u} & ({'|'.join(n1_list)}) & ({'|'.join(n2_list)}))")

    return '(n1!=n2) & (' + (' | '.join(u_list)) + ')'