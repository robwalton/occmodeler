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
        rows, columns=['time', 'type', 'name', 'num', 'count'])


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
        data={'time': [0], 'type': ['place'], 'name': ['a_bc'], 'num': ['3'], 'count': [1]},
        columns=['time', 'type', 'name', 'num', 'count']
    )
    assert_frame_equal(tidy_frame, desired_frame)


def test_filter_by_name_with_all_names(tidy_frame):
    frame = tidydata.filter_by_name(tidy_frame, ['a', 'b'])
    assert_frame_equal(frame, tidy_frame)


def test_filter_by_name_b(tidy_frame):
    frame = tidydata.filter_by_name(tidy_frame, ['b'])

    desired = pd.DataFrame(
        [[0, 'place', 'b', pd.np.nan, 4],
         [0, 'place', 'b', 'dot', 5]],
        columns=['time', 'type', 'name', 'num', 'count']
    )
    assert_frame_equal(frame, desired)


def log(thing):
    print('---')
    print(thing)
    print('---')

def test_generate_state_change_frame():
    in_rows = [
        # step, time, type, name, num, count
        [0, 0., 'place', 'a', 1, 1],
        [0, 0., 'place', 'a', 2, 1],
        [0, 0., 'place', 'b', 1, 0],
        [0, 0., 'place', 'b', 2, 0],
        #
        [1, 1., 'place', 'a', 1, 1],
        [1, 1., 'place', 'a', 2, 1],
        [1, 1., 'place', 'b', 1, 0],
        [1, 1., 'place', 'b', 2, 0],
        #
        [2, 2., 'place', 'a', 1, 0],
        [2, 2., 'place', 'a', 2, 1],
        [2, 2., 'place', 'b', 1, 1],
        [2, 2., 'place', 'b', 2, 0],
        #
        [3, 3., 'place', 'a', 1, 0],
        [3, 3., 'place', 'a', 2, 0],
        [3, 3., 'place', 'b', 1, 1],
        [3, 3., 'place', 'b', 2, 1],
        #
        [4, 4., 'place', 'a', 1, 1],
        [4, 4., 'place', 'a', 2, 0],
        [4, 4., 'place', 'b', 1, 0],
        [4, 4., 'place', 'b', 2, 1],
    ]
    in_frame = pd.DataFrame(
        in_rows, columns=['step', 'time', 'type', 'name', 'num', 'count'])

    desired_rows = [
        # 'step', 'time', 'type', 'name', 'num']
        [0, 0., 'place', 'a', 1],
        [0, 0., 'place', 'a', 2],
        [2, 2., 'place', 'b', 1],
        [3, 3., 'place', 'b', 2],
        [4, 4., 'place', 'a', 1],

    ]
    desired_frame = pd.DataFrame(
        desired_rows, columns=['step', 'time', 'type', 'name', 'num'])

    desired_frame = desired_frame.sort_values(by=['num', 'time'])
    actual_frame = tidydata.generate_state_change_frame(in_frame)
    log(desired_frame.reset_index())
    log(actual_frame.reset_index())
    assert_frame_equal(desired_frame.reset_index(), actual_frame.reset_index())


