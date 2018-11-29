import pandas as pd
from pandas.util.testing import assert_frame_equal

from pyspike import temporal


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
    actual_frame = temporal.generate_state_change_frame(in_frame)
    assert_frame_equal(desired_frame.reset_index(drop=True), actual_frame.reset_index(drop=True))


def log(thing):
    print('---')
    print(thing)
    print('---')


