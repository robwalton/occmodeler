# import time

import networkx as nx
import numpy as np
import plotly.graph_objs as go

import pyspike
from pyspike import tidydata
from pyspike.util import render_name


OPACITY = 0.5

# TODO: Nothing to see hear. Reconcile this file forked from network.py !

def _generate_medium_edge_trace(medium_graph, medium_layout):
    edge_x = []
    edge_y = []
    for e in medium_graph.edges:
        xy_start = medium_layout[e[0]]
        xy_end = medium_layout[e[1]]
        edge_x += [xy_start[0], xy_end[0], None]
        edge_y += [xy_start[1], xy_end[1], None]
    return dict( #go.Scatter(
        name='M',
        type='scatter',
        x=edge_x, y=edge_y,
        line=dict(color='#888'),
        hoverinfo='none',
        mode='lines'
    )


def _generate_plotly_node_data_trace_list(places, medium_layout, tstep, ordered_state_list, color_dict, diff_only=False,
                                          num_runs=1, place_offsets_dict={}):

    number_nodes = len(medium_layout)
    data = []
    sizeref = 1 if num_runs == 1 else (number_nodes / 100)
    places.sort_values('num', inplace=True)


    # if not diff_only:
        # Add each trace to data list
        # Create trace dict for each state with nodes of size 0

    nx_ = []
    ny = []
    nsize = []
    ntext = []
    for node_index in range(number_nodes):
        x, y = medium_layout[node_index]
        nx_.append(x)
        ny.append(y)
        nsize.append(1)
        ntext.append(str(node_index))

    for state_name in ordered_state_list:
        if state_name in place_offsets_dict:
            x_offset, y_offset = place_offsets_dict[state_name]
            nx_state = [xval + x_offset for xval in nx_]
            ny_state = [yval + y_offset for yval in ny]
        else:
            nx_state = nx_
            ny_state = ny
        #
        # medium_layout_for_state = {}
        # for node_name, xy in medium_layout.items():
        #     x, y = xy
        #     medium_layout_for_state[node_name] = (x + x_offset, y + y_offset)

        places_at_tstep = places.query(f"tstep == {tstep}")
        node_list = places_at_tstep.query(f"name == '{state_name}'")
        # print(node_list)
        if not (len(node_list) == number_nodes):
            print("time:", tstep)
            print("len(node_list):", len(node_list))
            print("number_nodes:", number_nodes)
            assert False

        trace_data = dict(
            name=render_name(state_name),
            x=nx_state,
            y=ny_state,
            mode='markers',
            hoverinfo='text',
            text=ntext,
            marker=dict(
                size=np.array(node_list['count']) * 400,
                sizeref=sizeref,  # TODO: change based on max value in series
                sizemode='area',
                # size=nsize,
                color=color_dict[state_name],  # opacity included here already
                line=dict(color='#888')
                # opacity=0.3

            )
        )
        data.append(trace_data)
    return data

    #     data.append(trace_data)
    # else:  # diff_only
    #     # add size data to each trace
    #     places_at_tstep = places.query(f"tstep == {tstep}")
    #
    #     for state_name in ordered_state_list:
    #         node_list = places_at_tstep.query(f"name == '{state_name}'")
    #         assert len(node_list) == number_nodes
    #         trace_data = dict(
    #             marker=dict(
    #                 size=np.array(node_list['count']) * 400
    #             )
    #         )
    #         data.append(trace_data)
    #
    # return data


def generate_network_figure(places, medium_graph, sacred_run, t):



    # start_time = time.time()
    state_name_list = list(places.name.unique())
    ordered_state_list, color_dict = pyspike.util.generate_state_order_and_colours(state_name_list, OPACITY)


    # Create initial edge trace to show layout
    pos = nx.get_node_attributes(medium_graph, 'pos')
    if pos:
        medium_layout = pos
    else:
        medium_layout = nx.spring_layout(medium_graph, dim=2)

    medium_edge_trace = _generate_medium_edge_trace(
        medium_graph, medium_layout)

    if 'offsets' in medium_graph.graph:
        # print(medium_graph.graph['offsets'])
        place_offsets_dict = medium_graph.graph['offsets']
    else:
        place_offsets_dict = {}

    sim_args = sacred_run.config['spike']['sim_args']
    num_runs = sim_args['runs']
    t_start = sim_args['interval']['start'],
    t_step = sim_args['interval']['step'],


    # TODO: We need to do this but why?
    if isinstance(t_start, tuple):
        t_start = t_start[0]

    if isinstance(t_step, tuple):
        t_step = t_step[0]


    # find step for time t
    tstep = round((t - t_start) / t_step)
    # places_at_time_t = places[np.isclose(places['time'], t)]
    # tstep = places_at_time_t['tstep'].iloc[0]
    print('tstep:', tstep)
    initial_node_traces = _generate_plotly_node_data_trace_list(
        places, medium_layout, tstep, ordered_state_list, color_dict, num_runs=num_runs,
        place_offsets_dict=place_offsets_dict)

    # tstep_list = places.tstep.unique()
    # t_list = places['time'].unique()
    # assert len(tstep_list) == len(t_list)
    # # start, stop, step = tidydata.determine_time_range_of_data_frame(places)
    # tstep_list.sort()
    #
    # sliders = [dict(
    #     active=10,
    #     currentvalue={"prefix": "Frequency: "},
    #     pad={"t": 50},
    #     steps=steps
    # )]

    fig = dict(
        data=[medium_edge_trace] + initial_node_traces,  # + node_trace_list + edge_trace_list,
        layout=go.Layout(
            # title=title,
            xaxis=dict(visible=False, scaleanchor='y'),
            yaxis=dict(visible=False),
            hovermode='closest',
            transition=dict(
                duration=0,
                easing='cubic-in-out'
            )
            # sliders=sliders,
        ),

    )
    return fig
