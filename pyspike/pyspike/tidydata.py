import pandas as pd

#%% Read and filter data


NODE_TYPES = ('place', 'transition')


def read_csv(filename, node_type, filter_name_list=None):
    """
    Reads a csv file created by spike with columns named according to:
    - Time --> time
    - a_2 --> a 2
    - a_dot --> a dot
    - a --> a NaN
    """

    assert node_type in NODE_TYPES
    raw_frame = pd.read_csv(filename, delimiter=';')
    frame = tidy_frame(raw_frame, node_type)

    # Filer by name if provided
    if filter_name_list:
        frame = filter_by_name(frame, list(filter_name_list))

    return frame


def tidy_frame(raw_frame, node_type):
    assert node_type in NODE_TYPES

    # r: gather(node, count, -Time)
    frame = pd.melt(raw_frame, id_vars=['Time'])
    frame['type'] = node_type

    # Expand variable name into name and node
    # r: separate(node, into = c("name", "num"), "sep" = "_(?!.*_)", fill = "right", extra = "merge")
    frame['name'], frame['num'] = frame['variable'].str.rsplit('_', 1).str
    del frame['variable']

    # msg not implemented in python yet
    # r: extract(node, c("name", "num", "msg"), "([^\\W_]+)(?:_+)([0-9]+)(?:_*)([^\\W_]+)*")

    # Reorder columns
    frame = frame.reindex(columns=['Time', 'type', 'name', 'num', 'value'])

    # Make Time lowercase
    frame.rename(columns={'Time': 'time', 'value': 'count'}, inplace=True)
    return frame
    # r: nodes$num < - as.integer(nodes$num)


def filter_by_name(frame, name_list):
    frame = frame.loc[frame['name'].isin(name_list)]
    frame.index = pd.Index(range(len(frame)))
    return frame


