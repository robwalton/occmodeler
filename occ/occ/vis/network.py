import time

import networkx as nx
import numpy as np
import plotly.graph_objs as go

import pyspike
from pyspike import tidydata, temporal
from pyspike.util import render_name


OPACITY = 0.5

def render_plot(medium_edge_trace, initial_node_traces, frames=[], tstep_for_each_frame=[], slider_step_list=[], run_id=None): #edge_trace_list, medium_edge_trace, node_trace_list):

    sliders_dict = {
        'active': 0,
        'yanchor': 'top',
        'xanchor': 'left',
        'currentvalue': {
            'font': {'size': 20},
            'prefix': 't: ',
            'visible': True,
            'xanchor': 'right'
        },
        'transition': {'easing': 'linear'},# removed duration: 0
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


def _generate_plotly_node_data_trace_list(places, medium_layout, tstep, ordered_state_list, color_dict, diff_only=False,
                                          num_runs=1, place_offsets_dict={}):

    number_nodes = len(medium_layout)
    data = []
    sizeref = 1 if num_runs == 1 else (number_nodes / 100)


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
            trace_data = dict(
                name=render_name(state_name),
                x=nx_state,
                y=ny_state,
                mode='markers',
                hoverinfo='text',
                text=ntext,
                marker=dict(
                    sizeref=sizeref,  # TODO: change based on max value in series
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


def generate_network_animation_figure_with_slider(places, medium_graph, medium_layout=None, run_id=None, num_runs=1):



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

    if 'offsets' in medium_graph.graph:
            print(medium_graph.graph['offsets'])
            place_offsets_dict = medium_graph.graph['offsets']
            # x_offset, y_offset = medium_graph.graph['offsets'][state_name]
            # medium_layout_for_state = {}
            # for node_name, xy in medium_layout.items():
            #     x, y = xy
            #     medium_layout_for_state[node_name] = (x + x_offset, y + y_offset)
    else:
        place_offsets_dict = {}

    initial_node_traces = _generate_plotly_node_data_trace_list(
        places, medium_layout, 0, ordered_state_list, color_dict, diff_only=False, num_runs=num_runs,
        place_offsets_dict=place_offsets_dict)

    # Remove all lines in places which are duplicate of those before

    place_changes = temporal.filter_place_changed_events(places)


    unique_tstep_list = place_changes.tstep.unique()
    unique_t_list = place_changes['time'].unique()
    complete_t_list = places['time'].unique()
    assert len(unique_tstep_list) == len(unique_t_list)

    unique_tstep_list.sort()
    tstep_number_of_repeated_frames = np.diff(unique_tstep_list).tolist()
    unique_t_list.sort()
    frame_list = []
    slider_step_list = []  # one per frame
    place_changes.sort_values('num', inplace=True)
    for tstep, t, repeated_frames in zip(unique_tstep_list, unique_t_list, tstep_number_of_repeated_frames):
        frame_data = _generate_plotly_node_data_trace_list(place_changes, medium_layout, tstep, ordered_state_list, color_dict,
                                                           diff_only=True, num_runs=num_runs)
        num_traces = len(ordered_state_list)
        assert len(frame_data) == num_traces

        for t_step_index in range(tstep, tstep + repeated_frames):
            frame_list.append({
                'data': frame_data,
                'name': str(int(t_step_index)),
                'traces': list(range(1, 1 + num_traces))
            })

            slider_step_list.append({
                'args': [
                    [str(int(t_step_index))],
                    {
                        'frame': {'duration': 100, 'redraw': False, 'easing': 'linear'},
                        'mode': 'immediate'
                    }
                ],
                'label': str(complete_t_list[t_step_index]),
                'value': str(complete_t_list[t_step_index]),
                'method': 'animate',
            })

    # print(f"generate_network_animation_figure_with_slider() ran in {time.time() - start_time} s")
    fig = render_plot(medium_edge_trace, initial_node_traces, frame_list, unique_tstep_list, slider_step_list, run_id)
    return fig
