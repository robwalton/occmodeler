import math
from collections import namedtuple, defaultdict

import networkx as nx
import pandas as pd
import numpy as np
import colorlover as cl



from pandas import DataFrame
import plotly.graph_objs as go

import pyspike
from pyspike.util import render_name


def generate_place_change_events(df):
    df.sort_values(by=['time'])
    change_frame_list = []

    for num in df.num.unique():
        for state_name in df.name.unique():
            df_num_name = df[(df.num == num) & (df.name == state_name)]
            df_num_name_changed = df_num_name[df_num_name['count'].diff() != 0]
            df_num_name_entered = df_num_name_changed[df_num_name_changed['count'] == 1]
            change_frame_list.append(df_num_name_entered)

    # concatenate
    df_out = pd.concat(change_frame_list)
    del df_out['count']
    df_out['num'] = pd.to_numeric(df['num'], downcast='integer')

    return df_out.sort_values(by=['time', 'name', 'num'])


def generate_transition_events(df):
    df = df[df['count'] > 0]
    return df.sort_values(by=['time', 'unit'])


class Occasion(namedtuple('Occasion', ['unit', 'state', 'time'])):

    def __repr__(self):
        return f"{self.state}{self.unit}@{self.time}"


def generate_causal_graph(place_change_events: DataFrame,
                          transition_events: DataFrame,
                          time_per_step: float):
    g = nx.DiGraph()  # Nodes are occasions and edges leading in their prehensions

    # Add the initial state for each node as an occasion with no past
    initial_occasions = place_change_events.query('tstep == 0')
    for occ in initial_occasions.itertuples():
        g.add_node(Occasion(int(occ.num), occ.name, occ.time))  # unit, state, time

    # Visit each transition and identify i) its output node and its 2 input nodes
    for trans in transition_events.itertuples():
        # row has: tstep, time, name, unit, neighbour & count

        # TODO: IS IT SAFE TO IGNORE THIS?
        # assert trans.count == 1  # Statistically likely to happen as simulations get more complex or are undersampled. Consider what to do if this occurs --Rob

        # Create new occasion in graph for this transition
        output_state = trans.name[1]  # ab -> b
        output_occasion = Occasion(int(trans.unit), output_state, trans.time)
        g.add_node(output_occasion)

        def choose_best_upstream_occasion(target_unit, target_state_name, source_time):
            query = f"num=={target_unit} & name=='{target_state_name}' & time<{source_time}"
            last_transition_time = place_change_events.query(query)['time'].max()
            if math.isnan(last_transition_time):
                #  Try including the source time
                query = f"num=={target_unit} & name=='{target_state_name}' & time=={source_time}"
                last_transition_time = place_change_events.query(query)['time'].min()
                if math.isnan(last_transition_time):
                    #  Try including the step after
                    query = f"num=={target_unit} & name=='{target_state_name}' & time<={source_time + time_per_step}"
                    last_transition_time = place_change_events.query(query)['time'].min()
            return Occasion(target_unit, target_state_name, last_transition_time)

        # Determine local input node from same unit
        state_name = trans.name[0]  # ab -> a
        local_input_occasion = choose_best_upstream_occasion(trans.unit, state_name, trans.time)

        # Determine input node from neighbour
        state_name = trans.name[1]  # ab -> b
        neighbour_input_occasion = choose_best_upstream_occasion(trans.neighbour, state_name, trans.time)

        # Add the two edges or _prehensions_
        g.add_edge(local_input_occasion, output_occasion)
        g.add_edge(neighbour_input_occasion, output_occasion)

    return g


    # def determine_earliest_unused_transition


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


def generate_causal_graph_figure(causal_graph, medium_graph, medium_layout=None, show_local_prehensions=True, z_scale=.2, run_id=None):
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
        else:
            medium_layout = nx.spring_layout(medium_graph, dim=2)



    # Create initial edge trace to show layout
    medium_edge_trace = _generate_medium_edge_trace(
        medium_graph, medium_layout)

    # Create a node list for occasions of each state, and edge list for edges leaving that stat
    def t_to_z(t):
        return t * z_scale
    occasion_by_state_dict = index_causal_graph_by_state(causal_graph)
    node_trace_list = []
    edge_trace_list = []

    for state_name in ordered_state_list:
        color = color_dict[state_name]
        occasion_list = occasion_by_state_dict[state_name]
        node_trace_list.append(
            generate_occasion_trace(occasion_list, color, medium_layout, t_to_z)
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
            generate_edge_trace(local_output_edge_list, color, medium_layout, t_to_z, state_name, dash='dot')
        )
        edge_trace_list.append(
            generate_edge_trace(neighbour_output_edge_list, color, medium_layout, t_to_z, state_name)
        )
    fig = render_plot(edge_trace_list, medium_edge_trace, node_trace_list, run_id)
    return fig


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


def generate_occasion_trace(occasion_list, color, medium_layout, t_to_z):
    nx_ = []
    ny = []
    nz = []
    state_name = occasion_list[0].state
    # print(f"{state_name} occasions are colour {color}")
    for occ in occasion_list:
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


def generate_edge_trace(output_edge_list, color, medium_layout, t_to_z, state_name, dash=None):
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
        P1 = [end[0], end[1], start[2]]
        P2 = P1
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


def extract_state_names_from_causal_graph(causal_graph):
    return set((occasion.state for occasion in causal_graph))


def extract_unit_numbers_from_causal_graph(causal_graph):
    return set((occasion.unit for occasion in causal_graph))


def index_causal_graph_by_state(causal_graph):
    d = defaultdict(list)
    for occasion in causal_graph:
        d[occasion.state].append(occasion)
    return d


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


