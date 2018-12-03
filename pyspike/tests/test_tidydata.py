import pandas as pd
import pytest
from pyspike import tidydata

from pandas.util.testing import assert_frame_equal


@pytest.fixture
def raw_columns():
    return ['Time', 'a', 'a_1', 'a_2', 'b', 'b_1']


@pytest.fixture()
def raw_frame(raw_columns):
    df = pd.DataFrame(
        data={raw_columns[i]: [i] for i in range(len(raw_columns))},
        columns=raw_columns,
    )
    df = df.astype({"Time": float})
    return df



@pytest.fixture()
def tidy_frame():
    rows = [
        [0., 'place', 'a', pd.np.nan, 1],
        [0., 'place', 'a', 1, 2],
        [0., 'place', 'a', 2, 3],
        [0., 'place', 'b', pd.np.nan, 4],
        [0., 'place', 'b', 1, 5],
    ]
    df = pd.DataFrame(
        rows, columns=['time', 'type', 'name', 'num', 'count'])
    df['num'] = pd.to_numeric(df['num'], downcast='integer')
    return df


def test_tidy(raw_frame, tidy_frame):
    frame = tidydata.tidy_frame(raw_frame, 'place')
    log('result', frame)
    log('desired', tidy_frame)
    assert_frame_equal(frame, tidy_frame)


def test_tidy_transitions():
    raw_columns = ['Time', 'a_1_10', 'a_2_20', 'b_3_20']
    raw_frame = pd.DataFrame(
        data={raw_columns[i]: [i] for i in range(len(raw_columns))},
        columns=raw_columns,
    )
    frame = tidydata.tidy_frame(raw_frame, 'transition')
    log(frame)
    assert list(frame.columns) == ['time', 'type', 'name', 'unit', 'neighbour', 'count']


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
    desired_frame = desired_frame.astype({"num": int})
    assert_frame_equal(tidy_frame, desired_frame)


def test_filter_by_name_with_all_names(tidy_frame):
    frame = tidydata.filter_by_name(tidy_frame, ['a', 'b'])
    assert_frame_equal(frame, tidy_frame)


def log(*thing_list):
    print('---')
    for thing in thing_list:
        print(thing)
    print('---')
