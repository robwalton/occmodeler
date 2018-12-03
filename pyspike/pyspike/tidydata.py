import pandas as pd
import numpy as np

#%% Read and filter data


NODE_TYPES = ('place', 'transition')


def read_csv(filename, node_type, filter_name_list=None, drop_non_coloured_sums=False):
    """
    Reads a csv file created by spike with columns named according to:
    - Time --> time
    - a_2 --> a 2
    - a_dot --> a dot
    - a --> a NaN
    """

    assert node_type in NODE_TYPES
    raw_frame = pd.read_csv(filename, delimiter=';')
    frame = tidy_frame(raw_frame, node_type, drop_non_coloured_sums)

    # Filer by name if provided
    if filter_name_list:
        frame = filter_by_name(frame, list(filter_name_list))

    return frame


def tidy_frame(raw_frame, node_type, drop_non_coloured_sums=False):
    assert node_type in NODE_TYPES

    # r: gather(node, count, -Time)
    frame = pd.melt(raw_frame, id_vars=['Time'])
    frame['type'] = node_type

    if node_type == 'place':
        # Expand variable name into name and node
        # r: separate(node, into = c("name", "num"), "sep" = "_(?!.*_)", fill = "right", extra = "merge")
        frame['name'], frame['num'] = frame['variable'].str.rsplit('_', 1).str
        del frame['variable']
        frame = frame.reindex(columns=['Time', 'type', 'name', 'num', 'value'])
        frame['Time'] = pd.to_numeric(frame['Time'], errors='coerce')
        frame['num'] = pd.to_numeric(frame['num'], errors='coerce')

        # frame = frame.astype({'num': np.int16, 'Time': float}, errors='coerce')

    if node_type == 'transition':
        # Expand variable name into name and node
        # r: separate(node, into = c("name", "num"), "sep" = "_(?!.*_)", fill = "right", extra = "merge")
        re_string = r"(?P<name>[^\W_]+)(?:_+)(?P<neighbour>[0-9]+)(?:_*)(?P<unit>[^\W_]+)*"
        new_col_frame = frame['variable'].str.extract(re_string)
        del frame['variable']
        frame['name'] = new_col_frame['name']
        frame['unit'] = new_col_frame['unit']
        frame['neighbour'] = new_col_frame['neighbour']
        frame = frame.reindex(columns=['Time', 'type', 'name', 'unit', 'neighbour', 'value'])
        # frame = frame.astype({'unit': int, 'neighbour': int, 'Time': float}, errors='ignore')
        frame['Time'] = pd.to_numeric(frame['Time'], errors='coerce')
        frame['unit'] = pd.to_numeric(frame['unit'], errors='coerce')
        frame['neighbour'] = pd.to_numeric(frame['neighbour'], errors='coerce')
    # msg not implemented in python yet
    # r: extract(node, c("name", "num", "msg"), "([^\\W_]+)(?:_+)([0-9]+)(?:_*)([^\\W_]+)*")

    # Reorder columns
    frame.rename(columns={'Time': 'time', 'value': 'count'}, inplace=True)

    if drop_non_coloured_sums:
        frame.dropna(inplace=True)

    return frame
    # r: nodes$num < - as.integer(nodes$num)


def filter_by_name(frame, name_list):
    frame = frame.loc[frame['name'].isin(name_list)]
    frame.index = pd.Index(range(len(frame)))
    return frame


def prepend_tidy_frame_with_tstep(places):
    # TODO: probably very slow!
    z = {v: i for i, v in enumerate(places['time'].unique())}
    places.insert(0, 'tstep', places['time'].map(z))
    return places


