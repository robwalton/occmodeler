import sys
import threading
import time

from pyspike.tidydata import generate_state_change_frame

sys.path.insert(0, "/Users/walton/dphil/proof-of-concept/src/pyspike")

from plotly.offline import init_notebook_mode, iplot, plot
import plotly.offline as py
import plotly.graph_objs as go
import networkx
import ipywidgets
import pandas as pd
import colorlover as cl
from ipywidgets import interactive, HBox, VBox, widgets
import numpy as np

import pyspike

py.init_notebook_mode(connected=True)


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


def plot_occasions(run_number, graph=None):

    # Load place data
    places = pyspike.tidydata.read_csv(
        filename=f"/Users/walton/dphil/proof-of-concept/runs/{run_number}/places.csv",
        node_type="place")
    places = places[pd.notnull(places['num'])]
    places['num'] = places['num'].astype(int)
    pyspike.tidydata.insert_step_column_based_on_unique_time_vals(places)
    places = places.sort_values(by=['time', 'num'])
    state_name_list = places['name'].unique()
    state_name_list.sort()

    # load graph (lazy dev only!)
    if not graph:
        G = networkx.read_gml(
            "/Users/walton/dphil/proof-of-concept/model/social/notebook/2018-11-22/1.gml",
            destringizer=int)
    else:
        G = graph

    # Layout graph (location will be used as location in x, y plane for occasions)
    layout = networkx.spring_layout(G, dim=2)

    # Create initial edge trace to show layout

    edge_x = []
    edge_y = []
    edge_z = []

    for e in G.edges:
        edge_x += [layout[e[0]][0], layout[e[1]][0], None]
        edge_y += [layout[e[0]][1], layout[e[1]][1], None]
        edge_z += [0, 0, None]

    edge_trace = go.Scatter3d(
        x=edge_x, y=edge_y, z=edge_z,
        line=dict(color='#888'), #width=0.5,
        hoverinfo='none',
        mode='lines'
    )

    # Create a trace of occasions by state_name and of same color

    color_list = cl.scales[str(len(state_name_list))]['qual']['Set1']
    color_list.reverse()

    all_occasions = generate_state_change_frame(places)

    def t_to_z(t):
        return t * 0.1

    node_trace_list = []

    for state_name, colorx in zip(state_name_list, color_list):
        print(f'{state_name} - {colorx}')
        ocs = all_occasions[all_occasions.name == state_name]
        nx = []
        ny = []
        nz = []
        for row in ocs.iterrows():
            t = row[1].time
            node_num = row[1].num
            x, y = layout[node_num]
            nx.append(x)
            ny.append(y)
            nz.append(t_to_z(t))
        node_trace_list.append(
            go.Scatter3d(
                x=nx,
                y=ny,
                z=nz,
                mode='markers',
                hoverinfo='text',
                text=list(G),  # gives names
                marker=dict(
                    # color=colorx,
                    # cmin=0,
                    # cmax=1,
                    size=10,
                    line=dict(width=2),
                    opacity=.5
                )
            )
        )
        node_trace_list.append(
            go.Scatter3d(
                x=nx,
                y=ny,
                z=nz,
                mode='markers',
                hoverinfo='text',
                text=list(G),  # gives names
                marker=dict(
                    # color=colorx,
                    # cmin=0,
                    # cmax=1,
                    size=10,
                    line=dict(width=2),
                    opacity=.5
                )
            )
        )

    py.plot(dict(
        data=[edge_trace] + node_trace_list,
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
