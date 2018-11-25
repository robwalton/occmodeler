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

    # Tidy
    frame = tidy_frame(raw_frame, node_type)

    # Filer by name if provided
    if filter_name_list:
        frame = filter_and_reindex_frame(frame, list(filter_name_list))

    return frame


    # places = places[['Time', 'prec'] + ['prec_' + str(i+1) for i in range(6)] + ['precbar'] + ['precbar_' + str(i+1) for i in range(6)]]
    # print(places)


def tidy_frame(raw_frame, node_type):
    assert node_type in NODE_TYPES

    # Melt
    frame = pd.melt(raw_frame, id_vars=['Time'])

    # Add type column
    frame['type'] = node_type

    # Expand variable name into name and node
    frame['name'], frame['node'] = frame['variable'].str.rsplit('_', 1).str
    del frame['variable']

    # Reorder columns
    frame = frame.reindex(columns=['Time', 'type', 'name', 'node', 'value'])

    # Make Time lowercase
    frame.rename(columns={'Time': 'time', 'value': 'count'}, inplace=True)
    return frame


def filter_and_reindex_frame(frame, name_list):
    frame = frame.loc[frame['name'].isin(name_list)]
    frame.index = pd.Index(range(len(frame)))
    return frame


