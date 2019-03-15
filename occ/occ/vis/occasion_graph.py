from enum import Enum

import networkx as nx
import numpy as np
import dash_core_components as dcc


import pyspike.model
from occ.reduction.occasion_graph import extract_state_names_from_causal_graph, index_causal_graph_by_state

expand_transition_name = pyspike.model.Transition.expand_name  # TODO: hmm

import plotly.graph_objs as go

import pyspike
from pyspike.util import render_name, check_medium_graph

NOAXIS = dict(
    title='',
    autorange=True,
    showgrid=False,
    zeroline=False,
    showline=False,
    ticks='',
    showticklabels=False,
    showspikes=False
)

# NOAXIS = {}

class Style(Enum):
    ORIG = 1
    SOFT = 2
    FOUNTAIN = 3


REVERSE_BARRED_ITEMS = False


def generate_causal_graph_figure(
        causal_graph, medium_graph, medium_layout=None, z_scale=1, run_id=None, style=Style.ORIG,
        return_dash_graph=False):
    # TODO: the z scale has no effect as plotly autofits entire structure
    # TODO: switch time to x axis?
    # determine state names and colours
    state_name_list = list(extract_state_names_from_causal_graph(causal_graph))
    ordered_state_list, color_dict = pyspike.util.generate_state_order_and_colours(state_name_list)

    # TODO: check unit numbering on both graphs for consistency

    # Layout medium graph
    # (location will be used as location in x, y plane for occasions)
    if not medium_layout:
        pos = nx.get_node_attributes(medium_graph, 'pos')
        if pos:
            medium_layout = pos
            print(pos)
        else:
            medium_layout = nx.spring_layout(medium_graph, dim=2)

    check_medium_graph(medium_graph)

    # Create initial edge trace to show layout
    medium_edge_trace = _generate_medium_edge_trace(
        medium_graph, medium_layout)

    # Create a node list for occasions of each state, and edge list for edges leaving that stat
    def t_to_z(t):
        return t * z_scale

    def t_to_z_reversed(t):
        return - t * z_scale

    occasion_by_state_dict = index_causal_graph_by_state(causal_graph)
    node_trace_list = []
    edge_trace_list = []

    for state_name in ordered_state_list:
        if 'offsets' in medium_graph.graph:
            # print(medium_graph.graph['offsets'])
            x_offset, y_offset = medium_graph.graph['offsets'][state_name]
            medium_layout_for_state = {}
            for node_name, xy in medium_layout.items():
                print('xy: ', xy)
                print(type(xy))
                x, y = xy[0], xy[1]
                medium_layout_for_state[node_name] = (x + x_offset, y + y_offset)
        else:
            medium_layout_for_state = medium_layout
        color = color_dict[state_name]
        occasion_list = occasion_by_state_dict[state_name]

        if REVERSE_BARRED_ITEMS and state_name.isupper():
            to_to_z_func = t_to_z_reversed
        else:
            to_to_z_func = t_to_z

        node_trace_list.append(
            generate_occasion_trace(occasion_list, color, medium_layout_for_state, to_to_z_func)
        )

        neighbour_output_edge_list = []
        local_output_edge_list = []
        # Add edges from each occasion
        for occ in occasion_list:
            edges = list(causal_graph.edges(occ))
            for edge in edges:
                if edge[1].unit == occ.unit:
                    local_output_edge_list.append(edge)
                else:
                    neighbour_output_edge_list.append(edge)
            # print(f"{occ} edges: {edge_list}")

        edge_trace_list.append(
            generate_edge_trace(
                local_output_edge_list, color, medium_layout_for_state, t_to_z, state_name, dash='dot', style=style)
        )
        edge_trace_list.append(
            generate_edge_trace(neighbour_output_edge_list, color, medium_layout_for_state, t_to_z, state_name, style=style)
        )

    fig_or_graph = render_plot(edge_trace_list, medium_edge_trace, node_trace_list, run_id)
    return fig_or_graph


def render_plot(edge_trace_list, medium_edge_trace, node_trace_list, run_id=None):
    title = f"Temporal graph for run {run_id}" if run_id else "Temporal graph"
    fig = go.Figure(dict(
        data=[medium_edge_trace] + node_trace_list + edge_trace_list,
        layout=go.Layout(
            title=title,
            # showlegend=False,
            hovermode='closest',
            scene=dict(
                xaxis=NOAXIS,
                yaxis=NOAXIS,
                zaxis=NOAXIS
            )
        )
    ))
    return fig


def create_dash_graph(edge_trace_list, medium_edge_trace, node_trace_list, run_id=None):
    title = f"Temporal graph for run {run_id}" if run_id else "Temporal graph"
    g = dcc.Graph(dict(
        data=[medium_edge_trace] + node_trace_list + edge_trace_list,
        layout=dcc.Layout(
            title=title,
            # showlegend=False,
            hovermode='closest',
            scene=dict(
                xaxis=NOAXIS,
                yaxis=NOAXIS,
                zaxis=NOAXIS
            )
        )
    ))
    return g


def generate_occasion_trace(occasion_list, color, medium_layout, t_to_z):
    nx_ = []
    ny = []
    nz = []
    state_name = occasion_list[0].state
    # print(f"{state_name} occasions are colour {color}")
    for occ in occasion_list:
        if occ.unit not in medium_layout:
            print('BREAKPONT HERE')
        x, y = medium_layout[occ.unit]
        nx_.append(x)
        ny.append(y)
        nz.append(t_to_z(occ.time))
        assert occ.state == state_name
    return go.Scatter3d(
        name=render_name(state_name),
        x=nx_,
        y=ny,
        z=nz,
        mode='markers',
        hoverinfo='text',
        text=list(occasion_list),  # gives names
        marker=dict(
            color=color,
            opacity=0.5,
            # size=15,
            # line=dict(width=5),
        ),
    )


def generate_edge_trace(output_edge_list, color, medium_layout, t_to_z, state_name, dash=None, style=Style.ORIG):
    edge_x = []
    edge_y = []
    edge_z = []

    for e in output_edge_list:
        assert e[0].state == state_name
        xy_start = medium_layout[e[0].unit]
        xy_end = medium_layout[e[1].unit]
        z_start = t_to_z(e[0].time)
        z_end = t_to_z(e[1].time)
        start = (xy_start[0], xy_start[1], z_start)
        end = (xy_end[0], xy_end[1], z_end)

        P0 = start

        if style == Style.ORIG:
            P1 = [end[0], end[1], start[2]]
            P2 = P1
        elif style == Style.SOFT:
            P1 = [start[0], start[1], end[2]]
            P2 = [end[0], end[1], start[2]]
        elif style == Style.FOUNTAIN:
            P1 = [start[0], start[1], end[2]]
            P2 = P1
        else:
            assert False
        P3 = end

        x, y, z = bezier_3d(P0, P1, P2, P3)
        edge_x += [None] + list(x)
        edge_y += [None] + list(y)
        edge_z += [None] + list(z)

    line_dict = dict(color=color)
    if dash:
        line_dict['dash'] = dash
    # dash options include 'dash', 'dot', and 'dashdot'
    trace = go.Scatter3d(
        name=render_name(state_name),
        x=edge_x, y=edge_y, z=edge_z,
        line=line_dict,  # width=8),  # width=0.5,
        hoverinfo='none',
        mode='lines',
    )


    return trace


def _generate_medium_edge_trace(medium_graph, medium_layout):
    edge_x = []
    edge_y = []
    edge_z = []
    for e in medium_graph.edges:
        xy_start = medium_layout[e[0]]
        xy_end = medium_layout[e[1]]
        edge_x += [xy_start[0], xy_end[0], None]
        edge_y += [xy_start[1], xy_end[1], None]
        edge_z += [0, 0, None]
    return go.Scatter3d(
        name='M',
        x=edge_x, y=edge_y, z=edge_z,
        line=dict(color='#888'),  # width=0.5,
        hoverinfo='none',
        mode='lines'
    )


def bezier(P0, P1, P2, P3, t=np.linspace(0, 1, 20)):
    return (
        (1 - t) ** 3 * P0 +
        3 * (1 - t) ** 2 * t * P1 +
        3 * (1 - t) * t * t * P2 +
        t ** 3 * P3
    )


def bezier_3d(P0, P1, P2, P3, t=np.linspace(0, 1, 20)):
    x = bezier(P0[0], P1[0], P2[0], P3[0], t=t)
    y = bezier(P0[1], P1[1], P2[1], P3[1], t=t)
    z = bezier(P0[2], P1[2], P2[2], P3[2], t=t)
    return x, y, z


