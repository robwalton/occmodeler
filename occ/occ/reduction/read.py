import pandas as pd

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

    raw_frame = pd.read_csv(filename, delimiter=';')

    if node_type == 'place':
        frame = tidy_places(raw_frame, drop_non_coloured_sums)
    elif node_type == 'transition':
        frame = tidy_transitions(raw_frame, drop_non_coloured_sums)
    else:
        raise TypeError(f"Unexpected type '{node_type}'")


    # Filer by name if provided
    if filter_name_list:
        frame = filter_by_name(frame, list(filter_name_list))

    return frame


def tidy_frame(raw_frame, node_type, drop_non_coloured_sums=False):
    assert node_type in NODE_TYPES




def tidy_places(raw_frame, drop_non_coloured_sums=False):
    frame = pd.melt(raw_frame, id_vars=['Time'])
    frame['type'] = 'place'
    # Expand variable name into name and node
    # r: separate(node, into = c("name", "num"), "sep" = "_(?!.*_)", fill = "right", extra = "merge")
    frame['name'], frame['num'] = frame['variable'].str.rsplit('_', 1).str
    del frame['variable']
    frame = frame.reindex(columns=['Time', 'type', 'name', 'num', 'value'])
    frame['Time'] = pd.to_numeric(frame['Time'], errors='coerce')
    frame['num'] = pd.to_numeric(frame['num'], errors='coerce')

    # frame = frame.astype({'num': np.int16, 'Time': float}, errors='coerce')
    if drop_non_coloured_sums:
        frame.dropna(inplace=True)
    frame.rename(columns={'Time': 'time', 'value': 'count'}, inplace=True)
    return frame



# The one below worked well for just the is_neighbour func, but was not ready for are_both_neighbours
# TRANSITION_COL_RE = r"(?P<name>[^\W_]+)(?:_+)(?P<neighbour>[0-9]+)(?:_*)(?P<unit>[^\W_]+)*"
TRANSITION_COL_RE = r"(?P<name>[^\W_]+)(?:_+)(?P<neighbour>[0-9]+)(?:_*)(?P<neighbour2>[0-9]+(?=(?:_+)[^\W_]+))*(?:_*)(?P<unit>[0-9]+)*"

def tidy_transitions(raw_frame, drop_non_coloured_sums=False):
    frame = pd.melt(raw_frame, id_vars=['Time'])
    frame['type'] = 'transition'
    # Expand variable name into name and node
        # r: separate(node, into = c("name", "num"), "sep" = "_(?!.*_)", fill = "right", extra = "merge")

    new_col_frame = frame['variable'].str.extract(TRANSITION_COL_RE)
    del frame['variable']
    frame['name'] = new_col_frame['name']
    frame['unit'] = new_col_frame['unit']
    frame['neighbour'] = new_col_frame['neighbour']
    frame['neighbour2'] = new_col_frame['neighbour2']
    frame = frame.reindex(columns=['Time', 'type', 'name', 'unit', 'neighbour', 'neighbour2', 'value'])
    # frame = frame.astype({'unit': int, 'neighbour': int, 'Time': float}, errors='ignore')
    frame['Time'] = pd.to_numeric(frame['Time'], errors='coerce')
    # Int columns can't have NaN!
    # See https://stackoverflow.com/questions/11548005/numpy-or-pandas-keeping-array-type-as-integer-while-having-a-nan-value
    frame['unit'] = pd.to_numeric(frame['unit'], errors='coerce')
    frame['neighbour'] = pd.to_numeric(frame['neighbour'], errors='coerce')
    frame['neighbour2'] = pd.to_numeric(frame['neighbour2'], errors='coerce')

    if drop_non_coloured_sums:
        frame.dropna(subset=['neighbour'], inplace=True)
    # msg not implemented in python yet
    # r: extract(node, c("name", "num", "msg"), "([^\\W_]+)(?:_+)([0-9]+)(?:_*)([^\\W_]+)*")

    # Reorder columns
    frame.rename(columns={'Time': 'time', 'value': 'count'}, inplace=True)
    return frame


def filter_by_name(frame, name_list):
    frame = frame.loc[frame['name'].isin(name_list)]
    frame.index = pd.Index(range(len(frame)))
    return frame


def determine_time_range_of_data_frame(df):
    time_values = list(df['time'].unique())
    time_values.sort()
    start = time_values[0]
    stop = time_values[-1]
    step = time_values[1] - time_values[0]
    return start, stop, step


def prepend_tidy_frame_with_tstep(frame):
    # TODO: probably very slow!
    z = {v: i for i, v in enumerate(frame['time'].unique())}
    frame.insert(0, 'tstep', frame['time'].map(z))
    return frame