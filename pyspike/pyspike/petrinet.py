from collections import defaultdict


import networkx as nx
import scipy as sp


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



# def graph_to_arc_expression(g):
#
#     predicate_token_pair_list = []
#
#     for x in sorted(g.adj.keys()):
#         for y in sorted(g.adj[x].keys()):
#             predicate_token_pair_list.append('[u={}]({},m)'.format(x, y))
#     return '++'.join(predicate_token_pair_list)

# colorfunctions:
# bool  is_neighbour(Unit u,Unit n) { (u=0 & (n=1|n=2|n=28|n=29)) | (u=1 & (n=0|n=2|n=3|n=29)) | (u=2 & (n=0|n=1|n=3|n=4|n=20|n=25)) | (u=3 & (n=1|n=2|n=4|n=6)) | (u=4 & (n=2|n=3|n=5|n=6)) | (u=5 & (n=4|n=6|n=7|n=10)) | (u=6 & (n=3|n=4|n=5|n=7|n=8|n=23)) | (u=7 & (n=5|n=6|n=8|n=9)) | (u=8 & (n=6|n=7|n=10|n=17)) | (u=9 & (n=7|n=10|n=11)) | (u=10 & (n=5|n=8|n=9|n=12)) | (u=11 & (n=9|n=12|n=13|n=21)) | (u=12 & (n=10|n=11|n=13|n=14)) | (u=13 & (n=11|n=12|n=14|n=15|n=18)) | (u=14 & (n=12|n=13|n=15|n=16)) | (u=15 & (n=13|n=14|n=16|n=17)) | (u=16 & (n=14|n=15|n=17|n=18)) | (u=17 & (n=8|n=15|n=16|n=18|n=19)) | (u=18 & (n=13|n=16|n=17|n=19|n=20)) | (u=19 & (n=17|n=18|n=21)) | (u=20 & (n=2|n=18|n=21)) | (u=21 & (n=11|n=19|n=20|n=22)) | (u=22 & (n=21|n=23|n=24)) | (u=23 & (n=6|n=22|n=25)) | (u=24 & (n=22|n=25|n=26)) | (u=25 & (n=2|n=23|n=24|n=27)) | (u=26 & (n=24|n=27|n=28)) | (u=27 & (n=25|n=26|n=28|n=29)) | (u=28 & (n=0|n=26|n=27|n=29)) | (u=29 & (n=0|n=1|n=27|n=28)) };


def generate_candl_file_from_template(candl_file_template_text, graph: nx.Graph):
    """
    candl_file_template must have the section:

        colorfunctions:
        bool  is_neighbour(Unit u,Unit n) {$FUNC$}

    It must also contain:

    colorsets:
      Unit = {$RANGE$};

    variables:
      Unit : u;
      Unit : n;


    Replace $FUNC$ with a function generated from the graph provided. 'u' stands for unit
    and 'n' for neighbour.

    :param candl_file_template_path:
    :param graph: an undirected networkx graph
    :return: contents of a completed .candl model file
    """

    if not graph.has_node(1):
        raise ValueError(f"Nodes must be labelled with integers. Use nx.convert_node_labels_to_integers().")

    if not graph.has_node(0):
        raise ValueError(f"Nodes must be indexed from 0. This keeps things simpler down the line!")

    is_neighbour_func_string = graph_to_is_neighbour_func(graph, unit_string='u', neighbour_sring='n1')
    are_both_neighbours_func_string = graph_to_are_both_neighbours_func(graph)
    if '$IS_NEIGHBOUR_FUNC$' not in candl_file_template_text:
        raise Exception("$IS_NEIGHBOUR_FUNC$ not found in candl_file_template_text")

    range_min = 0
    range_max = graph.number_of_nodes() - 1
    range_string = f"{range_min}..{range_max}"
    if '$RANGE$' not in candl_file_template_text:
        raise Exception("RANGE not found in candl_file_template_text")

    return candl_file_template_text.replace(
        '$IS_NEIGHBOUR_FUNC$', f' {is_neighbour_func_string} ').replace(
        '$ARE_BOTH_NEIGHBOURS_FUNC$', f' {are_both_neighbours_func_string} ').replace(
        '$RANGE$', range_string)









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


