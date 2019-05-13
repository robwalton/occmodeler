from pathlib import Path

import plotly.graph_objs as go

import pyspike
from occ.reduction import read
import pyspike.util

from pyspike.util import render_name


def generate_sums_by_state_figure(places_path: Path = None, places=None, run_id=None):
    if places_path:
        assert not places
        assert places_path.exists()
        places = read.read_csv(str(places_path), 'place', drop_non_coloured_sums=False)
    elif places is not None:
        assert not places_path
    else:
        raise ValueError("Only one of places_path or places should be set")
    non_coloured_sums = places[places.num.isna()]

    state_name_list = list(non_coloured_sums['name'].unique())
    ordered_state_list, color_dict = pyspike.util.generate_state_order_and_colours(state_name_list)

    data = []
    for state_name in ordered_state_list:
        color = color_dict[state_name]
        df = non_coloured_sums.query(f"name == '{state_name}'")
        df = df[df['count'].diff() != 0]
        data.append(
            go.Scatter(
                name=render_name(state_name),
                x=df['time'],
                y=df['count'],
                line=dict(
                    color=color,
                    # shape='hv'
                ),
                mode='lines+markers',
            )
        )
    title = f"Non coloured sums for run {run_id}" if run_id else "Non coloured sums"

    layout = go.Layout(
        title=title,
        yaxis=dict(title='count'),
        xaxis=dict(
            title='time',
            rangeslider=dict(
                visible=True
            ),
        ),
        clickmode='event+select',

    )

    # fig = go.Figure(data=data, layout=layout)
    # return fig
    return dict(data=data, layout=layout)
    # url = py.plot(fig)


def generate_online_dashboard():
    pass
# https://plot.ly/python/create-online-dashboard/


def generate_movie():
    pass

