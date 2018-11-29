import sys
import threading
import time

sys.path.insert(0, "/Users/walton/dphil/proof-of-concept/src/pyspike")

from plotly.offline import init_notebook_mode, iplot, plot
import plotly.offline as py
import plotly.graph_objs as go
import networkx as nx
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


def create_interactive_graph(run_number, graph=None, name_list=['a', 'b', 'c', 'C'], dim=3):

    places = pyspike.tidydata.read_csv(filename=f"/Users/walton/dphil/proof-of-concept/runs/{run_number}/places.csv", node_type="place")
    places = places[pd.notnull(places['num'])]
    places['num'] = places['num'].astype(int)
    pyspike.tidydata.insert_step_column_based_on_unique_time_vals(places)
    places = places.sort_values(by=['time', 'num'])
    if not graph:
        G = nx.read_gml("/Users/walton/dphil/proof-of-concept/model/social/notebook/2018-11-22/1.gml", destringizer=int)
    else:
        G = graph
    #G=nx.random_geometric_graph(200,0.125)
    #pos=nx.get_node_attributes(G,'pos')
    assert dim == 3
    layout = nx.spring_layout(G, dim=3)
    Xn = [layout[k][0] for k in range(len(G))]
    Yn = [layout[k][1] for k in range(len(G))]
    Zn = [layout[k][2] for k in range(len(G))]
    Xe = []
    Ye = []
    Ze = []
    for e in G.edges:
        Xe += [layout[e[0]][0], layout[e[1]][0], None]
        Ye += [layout[e[0]][1], layout[e[1]][1], None]
        Ze += [layout[e[0]][2], layout[e[1]][2], None]

    color_list = cl.scales[str(len(name_list))]['qual']['Set1']
    color_list.reverse()
    edge_trace = go.Scatter3d(
        x=Xe, y=Ye, z=Ze,
        line=dict(color='#888'), #width=0.5,
        hoverinfo='none',
        mode='lines'
    )

    node_trace_list = []
    for name, color in zip(name_list, color_list):
        node_trace_list.append(
            go.Scatter3d(
                x=Xn,
                y=Yn,
                z=Zn,
                mode='markers',
                hoverinfo='text',
                text=list(G),  # gives names
                marker=dict(
                    color=color,
                    cmin=0,
                    cmax=1,
                    size=10,
                    # line=dict(width = 2),
                )
            )
        )

    fig = go.FigureWidget(
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
    )

    def update_time(t, **enable_dict):
        start_time = time.perf_counter()

        def node_count_list(state_name):
            return places[((places.name == state_name) & np.isclose(places.time, t))]['count']

        for state_name, node_trace in zip(name_list, fig.data[1:]):
            node_trace.visible = enable_dict[state_name]
            if enable_dict[state_name]:
                node_trace['marker']['size'] = node_count_list(state_name) * 50
        print(time.perf_counter() - start_time)

    def update_step(step, **enable_dict):
        start_time = time.perf_counter()

        def node_count_list(state_name):
            return places[((places.name == state_name) & (places.step == step))]['count']

        for state_name, node_trace in zip(name_list, fig.data[1:]):
            if node_trace.visible:
                node_trace['marker']['size'] = node_count_list(state_name) * 50
        print(time.perf_counter() - start_time)

    enable_dict = {n: True for n in name_list}
    def update_visiblity(**enable_dict):
        for state_name, node_trace in zip(name_list, fig.data[1:]):
            node_trace.visible = enable_dict[state_name]



    # tslider = ipywidgets.FloatSlider(value=0,
    #                                  min=0,
    #                                  max=20.0,
    #                                  step=0.1,
    #                                  layout=ipywidgets.Layout(width='100%'))

    step_slider = ipywidgets.IntSlider(value=0,
                                     min=0,
                                     max=199,
                                     step=1,
                                     layout=ipywidgets.Layout(width='100%'))


    # knobs = interactive(update_time, t=tslider, **{n: True for n in name_list})

    step_control = interactive(update_step, step=step_slider)
    visible_control = interactive(update_visiblity, **enable_dict)



    play_control = ipywidgets.widgets.Play(
        min=0,
        max=199,
        step=1,
    )
    widgets.jslink((play_control, 'value'), (step_slider, 'value'))

    vb = VBox((HBox((visible_control, fig)), HBox((play_control, step_slider))))
    # vb.layout.align_items = 'center'
    return places, vb


    # def update_time(t):
    #     def node_count_list(state_name):
    #         return places[((places.name == state_name) & np.isclose(places.time, t))]['count']
    #
    #     for state_name, node_trace in zip(name_list, fig.data[1:]):
    #         node_trace['marker']['size'] = node_count_list(state_name) * 50
    #
    #
    # def update_step(step):
    #     def node_count_list(state_name):
    #         return places[((places.name == state_name) & places.step == step)]['count']
    #
    #     for state_name, node_trace in zip(name_list, fig.data[1:]):
    #         node_trace['marker']['size'] = node_count_list(state_name) * 50
    #
    # q = queue.Queue()
    #
    # def put_on_queue(t):
    #     q.put(t)
    #
    # tslider = widgets.FloatSlider(
    #     value=0,
    #     min=0,
    #     max=12.0,
    #     step=0.1,
    #     layout=ipywidgets.Layout(width='100%')
    # )
    #
    # ixslider = widgets.IntSlider(
    #     value=0,
    #     min=0,
    #     max=200,
    #     step=1,
    # )
    #
    # knobs = interactive(put_on_queue, t=tslider)
    #
    # def worker():
    #     while True:
    #         last_val = None
    #         while True:
    #             try:
    #                 last_val = q.get_nowait()
    #             except queue.Empty:
    #                 break
    #         if last_val is None:
    #             last_val = q.get()
    #         update_time(last_val)
    #         time.sleep(.5)
    #
    # thread = threading.Thread(target=worker)
    #
    # play = ipywidgets.widgets.Play(
    #     interval=300,
    #     min=0,
    #     max=200,
    #     step=1,
    #     description="Press play",
    #     disabled=False
    # )
    # widgets.jslink((play, 'value'), (tslider, 'value'))
    # vb = VBox((fig, tslider, play))
    # thread.start()
    #
    # return vb

import queue
import ipywidgets

class Thing(object):

    def __init__(self, update_func):
        self.update_func = update_func
        self._q = queue.Queue()
        self._thread = threading.Thread(target=self._worker)

    def start(self):
        self._thread.start()

    def __call__(self, t):
        self._q.put(t)

    def _worker(self):
        while True:
            last_val = None
            while True:
                try:
                    last_val = self._q.get_nowait()
                except queue.Empty:
                    break
            if last_val is None:
                last_val = self._q.get()
            self.update_func(last_val)

# import pyspike.plot
# import ipywidgets
# progress = ipywidgets.widgets.IntProgress(value=0.0, min=0, max=10)
# def update_progress(val):
#     progress.value = val
#     time.sleep(1)
# connector = pyspike.plot.Thing(update_progress)
# slider = interactive(connector.put_on_queue, a=(1, 10, 1))
# vb = HBox((slider, progress))
# connector.start()
# display(vb)


def test():
    q = queue.Queue()
    def put_on_queue(a):
        q.put(a)

    slider = interactive(put_on_queue, a=(1, 10, 1))

    import threading, time
    progress = ipywidgets.widgets.IntProgress(value=0.0, min=0, max=10)

    def worker():
        while True:
            last_val = None
            while True:
                try:
                    last_val = q.get_nowait()
                except queue.Empty:
                    break
            if last_val is None:
                last_val = q.get()
            progress.value = last_val
            time.sleep(1)

    #         print('last val: ' + str(last_val))

    thread = threading.Thread(target=worker)
    vb = HBox((slider, progress))
    thread.start()
    return vb




