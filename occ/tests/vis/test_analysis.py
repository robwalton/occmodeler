from pathlib import Path
import plotly.offline as py

from occ.vis.analysis import generate_sums_by_state_figure

from occ_test_files import RUN_71_PLACES

PLOT = True


def test_generate_sums_by_state_figure():
    fig = generate_sums_by_state_figure(Path(RUN_71_PLACES))
    if PLOT:
        url = py.plot(fig)
