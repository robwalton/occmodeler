from pathlib import Path


import plotly.offline as py
import plotly.graph_objs as go

import pyspike
from pyspike import tidydata
import pyspike.util

from pyspike.util import render_name


def generate_sums_by_state_figure(places_path: Path):

    assert places_path.exists()
    places = tidydata.read_csv(str(places_path), 'place', drop_non_coloured_sums=False)
    non_coloured_sums = places[places.num.isna()]

    state_name_list = list(non_coloured_sums['name'].unique())
    ordered_state_list, color_dict = pyspike.util.generate_state_order_and_colours(state_name_list)

    data = []
    for state_name in ordered_state_list:
        color = color_dict[state_name]
        df = non_coloured_sums.query(f"name == '{state_name}'")
        data.append(
            go.Scatter(
                name=render_name(state_name),
                x=df['time'],
                y=df['count'],
                line=dict(color=color)
            )
        )

    layout = go.Layout(
        title='Non coloured sums',
        yaxis=dict(title='count'),
        xaxis=dict(title='time')
    )

    fig = go.Figure(data=data, layout=layout)
    return fig
    # url = py.plot(fig)


def generate_online_dashboard():
    pass
# https://plot.ly/python/create-online-dashboard/


def generate_movie():
    pass

