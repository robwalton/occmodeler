from collections import namedtuple, defaultdict

import networkx as nx
import pandas as pd
import colorlover as cl


from pandas import DataFrame
import plotly.offline as py
import plotly.graph_objs as go


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
                          transition_events: DataFrame):
    g = nx.DiGraph()  # Nodes are occasions and edges leading in their prehensions

    # Add the initial state for each node as an occasion with no past
    initial_occasions = place_change_events.query('tstep == 0')
    for occ in initial_occasions.itertuples():
        g.add_node(Occasion(int(occ.num), occ.name, occ.time))  # unit, state, time

    # Visit each transition and identify i) its output node and its 2 input nodes
    for trans in transition_events.itertuples():
        # row has: tstep, time, name, unit, neighbour & count

        assert trans.count == 1  # Statistically likely to happen as simulations
        # get more complex or are undersampled. Condier what to do if this occurs --Rob

        # Create new occasion in graph for this transition
        output_state = trans.name[1]  # ab -> b
        output_occasion = Occasion(int(trans.unit), output_state, trans.time)
        g.add_node(output_occasion)

        # Determine local input node from same unit
        state_name = trans.name[0]  # ab -> a
        query = f"num=={trans.unit} & name=='{state_name}' & time<{trans.time}"
        last_transition_time = place_change_events.query(query)['time'].max()
        local_input_occasion = Occasion(trans.unit, state_name, last_transition_time)

        # Determine input node from neighbour
        state_name = trans.name[1]  # ab -> b
        query = f"num=={trans.neighbour} & name=='{state_name}' & time<{trans.time}"
        last_transition_time = place_change_events.query(query)['time'].max()
        neighbour_input_occasion = Occasion(trans.neighbour, state_name, last_transition_time)

        # Add the two edges or _prehensions_
        g.add_edge(local_input_occasion, output_occasion)
        g.add_edge(neighbour_input_occasion, output_occasion)

    return g


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


def plot_causal_graph(causal_graph, medium_graph, medium_layout=None):

    # determine state names and colours
    state_name_list = list(extract_state_names_from_causal_graph(causal_graph))
    state_name_list.sort()
    color_list = cl.scales['9']['qual']['Set1']
    color_list = color_list[:len(state_name_list)]
    color_list.reverse()

    # TODO: check unit numbering on both graphs for consistency

    # Layout medium graph
    # (location will be used as location in x, y plane for occasions)
    if not medium_layout:
        medium_layout = nx.spring_layout(medium_graph, dim=2)

    # Create initial edge trace to show layout
    medium_edge_trace = _generate_medium_edge_trace(
        medium_graph, medium_layout)

    # Create a node list for occasions of each state, and edge list for edges leaving that stat
    def t_to_z(t):
        return t * 0.3
    occasion_by_state_dict = index_causal_graph_by_state(causal_graph)
    node_trace_list = []
    edge_trace_list = []

    for state_name, color in zip(state_name_list, color_list):
        occasion_list = occasion_by_state_dict[state_name]
        node_trace_list.append(
            generate_occasion_trace(occasion_list, color, medium_layout, t_to_z)
        )

        output_edge_list = []
        # Add edges from each occasion
        for occ in occasion_list:
            edges = list(causal_graph.edges(occ))
            for edge in edges:
                if edge[1].unit != occ.unit:
                    output_edge_list.append(edge)
            # print(f"{occ} edges: {edge_list}")

        edge_trace_list.append(
            generate_edge_trace(output_edge_list, color, medium_layout, t_to_z)
        )

    render_plot(edge_trace_list, medium_edge_trace, node_trace_list)


def render_plot(edge_trace_list, medium_edge_trace, node_trace_list):
    py.plot(dict(
        data=[medium_edge_trace] + node_trace_list + edge_trace_list,
        layout=go.Layout(
            showlegend=False,
            hovermode='closest',
            scene=dict(
                xaxis=NOAXIS,
                yaxis=NOAXIS,
                zaxis=NOAXIS
            )
        )
    ), auto_open=True)


def generate_occasion_trace(occasion_list, color, medium_layout, t_to_z):
    nx_ = []
    ny = []
    nz = []
    for occ in occasion_list:
        x, y = medium_layout[occ.unit]
        nx_.append(x)
        ny.append(y)
        nz.append(t_to_z(occ.time))
    return go.Scatter3d(
        x=nx_,
        y=ny,
        z=nz,
        mode='markers',
        hoverinfo='text',
        text=list(occasion_list),  # gives names
        marker=dict(
            color=color,
            opacity=0.7,
            size=15,
            line=dict(width=5),
        ),
    )


def generate_edge_trace(output_edge_list, color, medium_layout, t_to_z):
    edge_x = []
    edge_y = []
    edge_z = []
    for e in output_edge_list:
        xy_start = medium_layout[e[0].unit]
        xy_end = medium_layout[e[1].unit]
        z_start = t_to_z(e[0].time)
        z_end = t_to_z(e[1].time)
        edge_x += [xy_start[0], xy_end[0], None]
        edge_y += [xy_start[1], xy_end[1], None]
        edge_z += [z_start, z_end, None]
    return go.Scatter3d(
        x=edge_x, y=edge_y, z=edge_z,
        line=dict(color=color, width=8),  # width=0.5,
        hoverinfo='none',
        mode='lines'
    )


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

