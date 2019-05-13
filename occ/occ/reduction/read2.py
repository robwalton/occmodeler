import occ.reduction.occasion_graph

# import generate_place_increased_events, generate_transition_events, generate_causal_graph, filter_place_changed_events



import pandas as pd

import occ.reduction.read


### Places

def load_tidy_places(places_csv_path, filter_name_list=None, drop_non_coloured_sums=False):
    raw_places_frame = load_places(places_csv_path)
    return tidy_places(raw_places_frame)


def load_places(places_csv_path):
    places = pd.read_csv(places_csv_path, delimiter=';')
    # places = pyspike.tidydata.read_csv(filename=str(places_csv_path), node_type="place", drop_non_coloured_sums=False)
    places = prepend_tidy_frame_with_tstep(places)
    return places


def tidy_places(raw_places_frame, filter_name_list=None, drop_non_coloured_sums=False):
    frame = occ.reduction.read.tidy_frame(raw_places_frame, 'place', drop_non_coloured_sums)
    # Filer by name if provided
    if filter_name_list:
        frame = occ.reduction.read.filter_by_name(frame, list(filter_name_list))
    return frame


def filter_changed_places(tidy_places_frame):
    place_changes = occ.reduction.occasion_graph.filter_place_changed_events(tidy_places_frame)
    place_changes.sort_values('tstep')
    return place_changes


### Transitions


def load_tidy_transitions(transitions_csv_path, filter_name_list=None, drop_non_coloured_sums=False):
    raw_transitions_frame = load_transitions(transitions_csv_path)
    return tidy_transitions(raw_transitions_frame)


def load_transitions(transitions_csv_path):
    transitions = pd.read_csv(transitions_csv_path, delimiter=';')
    # transitions = pyspike.tidydata.read_csv(filename=str(transitions_csv_path), node_type="transition", drop_non_coloured_sums=False)
    transitions = prepend_tidy_frame_with_tstep(transitions)
    return transitions


def tidy_transitions(raw_transitions_frame, filter_name_list=None, drop_non_coloured_sums=False):
    frame = occ.reduction.read.tidy_frame(raw_transitions_frame, 'transition', drop_non_coloured_sums)
    # Filer by name if provided
    if filter_name_list:
        frame = occ.reduction.read.filter_by_name(frame, list(filter_name_list))
    return frame


def filter_changed_transitions(tidy_transitions_frame):
    return occ.reduction.occasion_graph.generate_transition_events(tidy_transitions_frame)

### Causal graph






# def tidy_transitions(filename=None, raw_transitions_frame=None, filter_name_list=None, drop_non_coloured_sums=False):
#     assert filename or raw_transitions_frame
#     if filename:
#         raw_transitions_frame = pd.read_csv(filename, delimiter=';')
#     frame = pyspike.tidydata.tidy_frame(raw_transitions_frame, 'transition', drop_non_coloured_sums)
#     if filter_name_list:
#         frame = pyspike.tidydata.filter_by_name(frame, list(filter_name_list))
#     return frame


def prepend_tidy_frame_with_tstep(frame):
    # TODO: probably very slow!
    z = {v: i for i, v in enumerate(frame['time'].unique())}
    frame.insert(0, 'tstep', frame['time'].map(z))
    return frame
