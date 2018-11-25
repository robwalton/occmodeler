import pandas as pd
import pytest
from pyspike import tidydata

from pandas.util.testing import assert_frame_equal


@pytest.fixture
def raw_columns():
    return ['Time', 'a', 'a_1', 'a_2', 'b', 'b_dot']


@pytest.fixture()
def raw_frame(raw_columns):
    return pd.DataFrame(
        data={raw_columns[i]: [i] for i in range(len(raw_columns))},
        columns=raw_columns,
    )


@pytest.fixture()
def tidy_frame():
    rows = [
        [0, 'place', 'a', pd.np.nan, 1],
        [0, 'place', 'a', '1', 2],
        [0, 'place', 'a', '2', 3],
        [0, 'place', 'b', pd.np.nan, 4],
        [0, 'place', 'b', 'dot', 5],
    ]
    return pd.DataFrame(
        rows, columns=['time', 'type', 'name', 'node', 'count'])


def test_tidy(raw_frame, tidy_frame):
    frame = tidydata.tidy_frame(raw_frame, 'place')
    assert_frame_equal(frame, tidy_frame)


def test_tidy_with_underscore_name():

    input_frame = pd.DataFrame(
        data={'Time': [0], 'a_bc_3': [1]},
        columns=['Time', 'a_bc_3'],
    )
    tidy_frame = tidydata.tidy_frame(input_frame, 'place')

    desired_frame = pd.DataFrame(
        data={'time': [0], 'type': ['place'], 'name': ['a_bc'], 'node': ['3'], 'count': [1]},
        columns=['time', 'type', 'name', 'node', 'count']
    )
    assert_frame_equal(tidy_frame, desired_frame)


def test_filter_by_name_with_all_names(tidy_frame):
    frame = tidydata.filter_and_reindex_frame(tidy_frame, ['a', 'b'])
    assert_frame_equal(frame, tidy_frame)


def test_filter_by_name_b(tidy_frame):
    frame = tidydata.filter_and_reindex_frame(tidy_frame, ['b'])

    desired = pd.DataFrame(
        [[0, 'place', 'b', pd.np.nan, 4],
         [0, 'place', 'b', 'dot', 5]],
        columns=['time', 'type', 'name', 'node', 'count']
    )
    assert_frame_equal(frame, desired)





# Time;preb;prec_3;prea_6;tx_extbar;prec_6;rxa_4;precbar_6;prec;prea_2;prea_1;tx_exta_dot;prec_5;preb_4;rxa;rxb_3;tx_extb_dot;tx_exta;preb_1;rxbbar_2;prea_3;precbar;tx_extb;rxa_1;prea;prea_4;rxbbar_1;rxa_2;prea_5;precbar_2;precbar_5;rxb_1;precbar_1;preb_3;prec_2;preb_5;preb_2;prec_4;precbar_4;preb_6;rxb_5;prec_1;precbar_3;rxbbar_3;rxa_5;rxa_3;rxbbar;rxb_6;rxa_6;rxb;rxbbar_5;rxb_4;rxbbar_6;rxb_2;rxbbar_4;tx_extbar_dot

# Time;tbbar;ta_5;ta;extb;ta_6;ta_4;ta_1;tb;ta_3;tb_3;tb_5;extbbar;tbbar_5;tbbar_2;ta_2;tb_1;extbbar_constant;tbbar_3;exta_constant;tbbar_6;tbbar_1;tb_2;exta;tbbar_4;tb_4;tb_6;extb_constant


