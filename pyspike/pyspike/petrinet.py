from collections import defaultdict


import networkx as nx
import scipy as sp


def graph_to_func(g, unit_string='x', neighbour_sring='y'):

    x_list = []

    for x in sorted(g.adj.keys()):
        y_list = []
        for y in sorted(g.adj[x].keys()):
            y_list.append('{}={}'.format(neighbour_sring, y))
        if y_list:
            x_list.append(
                '({}={} & ({}))'.format(unit_string, x, '|'.join(y_list)))

    return ' | '.join(x_list)


def graph_to_arc_expression(g):

    predicate_token_pair_list = []

    for x in sorted(g.adj.keys()):
        for y in sorted(g.adj[x].keys()):
            predicate_token_pair_list.append('[u={}]({},m)'.format(x, y))
    return '++'.join(predicate_token_pair_list)

# def graph_to_arc_expression(g):

#     x_list = []

#     for x in sorted(g.adj.keys()):
#         y_list = []
#         for y in sorted(g.adj[x].keys()):
#             y_list.append('({},m)'.format(y))
#         if y_list:
#             x_list.append(
#                 '[u={}]({})'.format(x, '++'.join(y_list)))

#     return ' ++ '.join(x_list)


