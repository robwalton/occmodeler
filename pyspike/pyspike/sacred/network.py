import networkx as nx
import plotly.offline as pl
import plotly.graph_objs as go
from IPython.display import display, HTML

import pyspike
from pyspike import read_csv, tidydata
from pyspike.util import render_name
from tests.files import RUN_71_PLACES, RUN_71_TRANSITIONS, RUN_71_NETWORK_GML


def render_plot(medium_edge_trace, initial_node_traces, frames=[], tstep_for_each_frame=[], slider_step_list=[]): #edge_trace_list, medium_edge_trace, node_trace_list):

    sliders_dict = {
        'active': 0,
        'yanchor': 'top',
        'xanchor': 'left',
        'currentvalue': {
            'font': {'size': 20},
            'prefix': 'text-before-value-on-display',
            'visible': True,
            'xanchor': 'right'
        },
        'transition': {'duration': 300, 'easing': 'cubic-in-out'},
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
                    'args': [None, {'frame': {'duration': 500, 'redraw': False},
                                    'fromcurrent': True,
                                    'transition': {'duration': 300, 'easing': 'quadratic-in-out'}}],
                    'label': 'Play',
                    'method': 'animate'
                },
                {
                    'args': [[None], {'frame': {'duration': 0, 'redraw': False}, 'mode': 'immediate',
                                      'transition': {'duration': 0}}],
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




    return go.Figure(
        data=[medium_edge_trace] + initial_node_traces,  # + node_trace_list + edge_trace_list,
        layout=go.Layout(
            xaxis=dict(visible=False, scaleanchor='y'),
            yaxis=dict(visible=False),
            hovermode='closest',
            # sliders=sliders,
            sliders=[sliders_dict],
            updatemenus=updatemenus
        ),
        frames=frames
    )


def generate_medium_edge_trace(medium_graph, medium_layout):
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


def generate_plotly_node_data_trace_list(places, medium_layout, tstep, ordered_state_list, color_dict, diff_only=False):

    data = []

    if not diff_only:
    # Add each trace to data list
        for state_name in ordered_state_list:
            node_list = places.query(f"tstep == {tstep} & name == '{state_name}'")
            nx_ = []
            ny = []
            nsize = []
            ntext = []
            for node in node_list.itertuples():
                x, y = medium_layout[int(node.num)]
                nx_.append(x)
                ny.append(y)
                nsize.append(node.count)
                ntext.append(str(int(node.num)))

            trace_data = dict(
                name=render_name(state_name),
                x=nx_,
                y=ny,
                mode='markers',
                hoverinfo='text',
                text=ntext,
                marker=dict(
                    sizeref=0.01,
                    sizemode='area',
                    size=nsize,
                    color=color_dict[state_name],
                )
            )
            data.append(trace_data)
    if diff_only:
        for state_name in ordered_state_list:
            node_list = places.query(f"tstep == {tstep} & name == '{state_name}'")
            nx_ = []
            ny = []
            nsize = []
            ntext = []
            for node in node_list.itertuples():
                x, y = medium_layout[int(node.num)]
                nx_.append(x)
                ny.append(y)
                nsize.append(node.count)
                ntext.append(str(int(node.num)))

            trace_data = dict(
                name=render_name(state_name),
                x=nx_,
                y=ny,
                mode='markers',
                hoverinfo='text',
                text=ntext,
                marker=dict(
                    sizeref=0.01,
                    sizemode='area',
                    size=nsize,
                    color=color_dict[state_name],
                )
            )
            data.append(trace_data)
    return data


places = read_csv(RUN_71_PLACES, 'place', drop_non_coloured_sums=True)
places = tidydata.prepend_tidy_frame_with_tstep(places)
transitions = read_csv(RUN_71_TRANSITIONS, 'transition', drop_non_coloured_sums=True)
transitions = tidydata.prepend_tidy_frame_with_tstep(transitions)

medium_graph = nx.read_gml(RUN_71_NETWORK_GML, destringizer=int)

medium_layout = nx.spring_layout(medium_graph, dim=2)
state_name_list = list(places.name.unique())
ordered_state_list, color_dict = pyspike.util.generate_state_order_and_colours(state_name_list)

# Create initial edge trace to show layout
medium_edge_trace = generate_medium_edge_trace(
    medium_graph, medium_layout)


initial_node_traces = generate_plotly_node_data_trace_list(
    places, medium_layout, 0, ordered_state_list, color_dict, diff_only=False)


tstep_list = places.tstep.unique()
tstep_list.sort()
tstep_list = tstep_list[0:60:10]
# trace_names = [render_name(n) for n in ordered_state_list]
frames = []
sliders_step_list = []  # one per frame
for tstep in tstep_list:
    frame_data = generate_plotly_node_data_trace_list(
        places, medium_layout, tstep, ordered_state_list, color_dict, diff_only=False)
    frames.append({'data': frame_data, 'name': str(int(tstep)), 'traces': list(range(1, 5))})
    slider_step = {
        'args': [
            [int(tstep)],
            {'frame': {'duration': 300, 'redraw': False},
             'mode': 'immediate',
             'transition': {'duration': 300}}
        ],
        'label': str(int(tstep)),
        'method': 'animate',
    }
    sliders_step_list.append(slider_step)

fig = render_plot(medium_edge_trace, initial_node_traces, frames, tstep_list, sliders_step_list)
pl.plot(fig)

# figure = {'data': [{'x': [0, 1],
#                     'y': [0, 1],
#                     'mode': 'markers',
#                     'marker': {'sizeref':0.1, 'sizemode': 'area', 'size': [10, 20]},}],
#           'layout': {'xaxis': {'range': [0, 5], 'autorange': False},
#                      'yaxis': {'range': [0, 5], 'autorange': False},
#                      'title': 'Start Title',
#                      'updatemenus': [{'type': 'buttons',
#                                       'buttons': [{'label': 'Play',
#                                                    'method': 'animate',
#                                                    'args': [None]}]}]
#                     },
#           'frames': [{'data': [{'marker': {'sizemode': 'area', 'size': [30, 40]}}]},
#                      {'data': [{'marker': {'sizemode': 'area', 'size': [40, 50]}}]},
#                      {'data': [{'marker': {'sizemode': 'area', 'size': [60, 70]}}],
#                       'layout': {'title': 'End Title'}}]}
#
#


