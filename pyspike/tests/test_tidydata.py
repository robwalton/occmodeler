import pandas as pd
import pytest
import re


from pyspike import tidydata

from pandas.util.testing import assert_frame_equal

import tests.files
from pyspike.tidydata import TRANSITION_COL_RE


def log(*thing_list):
    print('---')
    for thing in thing_list:
        print(thing)
    print('---')


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


def test_tidy_places(raw_frame, tidy_frame):
    frame = tidydata.tidy_frame(raw_frame, 'place')
    log('result', frame)
    log('desired', tidy_frame)
    assert_frame_equal(frame, tidy_frame)


def test_prepend_tidy_frame_with_tstep():
    f_in = pd.DataFrame()
    f_in['time'] = pd.Series([0., 0., .1, .1, .2, .2])
    f_in['x'] = pd.Series([1, 2, 3, 4, 5, 6])
    desired = f_in.copy()
    desired.insert(0, 'tstep', pd.Series([0, 0, 1, 1, 2, 2]))
    actual = tidydata.prepend_tidy_frame_with_tstep(f_in)
    log('desired:', desired)
    assert_frame_equal(actual, desired)


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


class TestTransitionReString:

    # NOTE: This regex stuff is getting out of had. Pandas may well let use s function for this instead of a regex.

    def never_worked__test_with__state(self):
        m = re.match(TRANSITION_COL_RE, 'a')
        assert m.groupdict() == {}

    def never_worked__test_with__state_unit(self):
        m = re.match(TRANSITION_COL_RE, 'a_1')
        assert m.groupdict() == {}

    def test_with__state_neighbour_unit(self):
        m = re.match(TRANSITION_COL_RE, 'a_1_2')
        assert m.groupdict() == {'name': 'a', 'neighbour': '1', 'neighbour2': None, 'unit': '2'}
        m = re.match(TRANSITION_COL_RE, 'a_12_34')
        assert m.groupdict() == {'name': 'a', 'neighbour': '12', 'neighbour2': None, 'unit': '34'}
        # assert m.groupdict() == {'name': 'a', 'neighbour': '1', 'unit': '2'}


    def test_with__state_neighbour_neighbour2_unit(self):
        m = re.match(TRANSITION_COL_RE, 'a_1_2_3')
        assert m.groupdict() == {'name': 'a', 'neighbour': '1', 'neighbour2': '2', 'unit': '3'}


class TestLoadTransitions:

    def test_with__is_neighbour_func_used(self):
        raw_columns = ['Time', 'a_1_10', 'a_2_20', 'b_3_20']
        raw_frame = pd.DataFrame(
            data={raw_columns[i]: [i] for i in range(len(raw_columns))},
            columns=raw_columns,
        )
        frame = tidydata.tidy_frame(raw_frame, 'transition')
        log(frame)
        assert list(frame.columns) == ['time', 'type', 'name', 'unit', 'neighbour', 'neighbour2', 'count']

    def test_with_are_both_neighbours__func_used(self):
        transitions = tidydata.read_csv(tests.files.RUN_90_TRANSITIONS, 'transition')
        log([transitions])


if __name__ == '__main__':
    raw_frame = pd.read_csv(tests.files.RUN_90_TRANSITIONS, delimiter=';')
    frame = tidydata.tidy_frame(raw_frame, 'transition')



# def test_determine_time_range_of_data_frame(big_example_frame):
#     start, stop, step = tidydata.determine_time_range_of_data_frame(big_example_frame)
#     assert start == 0
#     assert stop == 4
#     assert step == 1



