import time

import networkx as nx
import numpy as np
import plotly.graph_objs as go

import pyspike
from pyspike import tidydata
from pyspike.util import render_name


OPACITY = 0.5

def render_plot(medium_edge_trace, initial_node_traces, frames=[], tstep_for_each_frame=[], slider_step_list=[], run_id=None): #edge_trace_list, medium_edge_trace, node_trace_list):

    sliders_dict = {
        'active': 0,
        'yanchor': 'top',
        'xanchor': 'left',
        'currentvalue': {
            'font': {'size': 20},
            'prefix': 'tstep: ',
            'visible': True,
            'xanchor': 'right'
        },
        'transition': {'duration': 0, 'easing': 'linear'},
        'pad': {'b': 10, 't': 50},
        'len': 0.9,
        'x': 0.1,
        'y': 0,
        'steps': slider_step_list
    }

    updatemenus = [
        {
            'buttons': [
                {
                    'args': [None, {'frame': {'duration': 0, 'redraw': False},
                                    'fromcurrent': True,
                                    'transition': {'duration': 0, 'easing': 'linear'}}],
                    'label': 'Play',
                    'method': 'animate'
                },
                {
                    'args': [[None], {'frame': {'duration': 500, 'redraw': False}, 'mode': 'immediate',
                                      'transition': {'duration': 500}}],
                    'label': 'Pause',
                    'method': 'animate'
                }
            ],
            'direction': 'left',
            'pad': {'r': 10, 't': 87},
            'showactive': False,
            'type': 'buttons',
            'x': 0.1,
            'xanchor': 'right',
            'y': 0,
            'yanchor': 'top'
        }
    ]
    title = f"Network state for run {run_id}" if run_id else "Network state"
    return go.Figure(
        data=[medium_edge_trace] + initial_node_traces,  # + node_trace_list + edge_trace_list,
        layout=go.Layout(
            title=title,
            xaxis=dict(visible=False, scaleanchor='y'),
            yaxis=dict(visible=False),
            hovermode='closest',
            # sliders=sliders,
            sliders=[sliders_dict],
            updatemenus=updatemenus
        ),
        frames=frames
    )


def _generate_medium_edge_trace(medium_graph, medium_layout):
    edge_x = []
    edge_y = []
    for e in medium_graph.edges:
        xy_start = medium_layout[e[0]]
        xy_end = medium_layout[e[1]]
        edge_x += [xy_start[0], xy_end[0], None]
        edge_y += [xy_start[1], xy_end[1], None]
    return go.Scatter(
        name='M',
        x=edge_x, y=edge_y,
        line=dict(color='#888'),
        hoverinfo='none',
        mode='lines'
    )


def _generate_plotly_node_data_trace_list(places, medium_layout, tstep, ordered_state_list, color_dict, diff_only=False):

    number_nodes = len(medium_layout)
    data = []

    if not diff_only:
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
            trace_data = dict(
                name=render_name(state_name),
                x=nx_,
                y=ny,
                mode='markers',
                hoverinfo='text',
                text=ntext,
                marker=dict(
                    sizeref=0.1,  # TODO: change based on max value in series
                    sizemode='area',
                    size=nsize,
                    color=color_dict[state_name],  # opacity included here already
                    line=dict(color='#888')
                    # opacity=0.3

                )
            )
            data.append(trace_data)
    else:  # diff_only
        # add size data to each trace
        places_at_tstep = places.query(f"tstep == {tstep}")

        for state_name in ordered_state_list:
            node_list = places_at_tstep.query(f"name == '{state_name}'")
            assert len(node_list) == number_nodes
            trace_data = dict(
                marker=dict(
                    size=np.array(node_list['count']) * 400
                )
            )
            data.append(trace_data)

    return data


def generate_network_animation_figure_with_slider(places, medium_graph, medium_layout=None, run_id=None):



    # start_time = time.time()
    state_name_list = list(places.name.unique())
    ordered_state_list, color_dict = pyspike.util.generate_state_order_and_colours(state_name_list, OPACITY)

    # Create initial edge trace to show layout
    if not medium_layout:
        pos = nx.get_node_attributes(medium_graph, 'pos')
        if pos:
            medium_layout = pos
        else:
            medium_layout = nx.spring_layout(medium_graph, dim=2)

    medium_edge_trace = _generate_medium_edge_trace(
        medium_graph, medium_layout)

    initial_node_traces = _generate_plotly_node_data_trace_list(
        places, medium_layout, 0, ordered_state_list, color_dict, diff_only=False)

    tstep_list = places.tstep.unique()
    t_list = places['time'].unique()
    assert len(tstep_list) == len(t_list)
    # start, stop, step = tidydata.determine_time_range_of_data_frame(places)
    tstep_list.sort()
    # tstep_list = tstep_list[0:60]
    # trace_names = [render_name(n) for n in ordered_state_list]
    frames = []
    sliders_step_list = []  # one per frame
    places.sort_values('num', inplace=True)
    for tstep, t in zip(tstep_list, t_list):
        frame_data = _generate_plotly_node_data_trace_list(
            places, medium_layout, tstep, ordered_state_list, color_dict, diff_only=True)
        num_traces = len(ordered_state_list)
        assert len(frame_data) == num_traces
        frames.append(
            {'data': frame_data,
             'name': str(int(tstep)),
             'traces': list(range(1, 1 + num_traces))})  # Leave first (medium) trace alone
        slider_step = {
            'args': [
                [int(tstep)],
                {
                    'frame': {'duration': 0, 'redraw': False, 'easing': 'linear'},
                    'mode': 'immediate'
                }
            ],
            'label': str(t),
            'method': 'animate',
        }

        sliders_step_list.append(slider_step)
    # print(f"generate_network_animation_figure_with_slider() ran in {time.time() - start_time} s")
    fig = render_plot(medium_edge_trace, initial_node_traces, frames, tstep_list, sliders_step_list, run_id)
    return fig
