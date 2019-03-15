import math
from collections import namedtuple, defaultdict

import networkx as nx
import pandas as pd

import pyspike.model

expand_transition_name = pyspike.model.Transition.expand_name  # TODO: hmm

from pandas import DataFrame


def generate_place_increased_events(df):
    '''

    :param df:
    :return:
    '''
    df.sort_values(by=['time'])
    change_frame_list = []

    for num in df.num.unique():
        for state_name in df.name.unique():
            df_num_name = df[(df.num == num) & (df.name == state_name)]
            df_num_name_changed = df_num_name[df_num_name['count'].diff() != 0]
            df_num_name_entered = df_num_name_changed[df_num_name_changed['count'] > 0]  #  chance will go up > 1
            change_frame_list.append(df_num_name_entered)

    # concatenate
    df_out = pd.concat(change_frame_list)
    del df_out['count']  # not required for current application and complicates tests
    df_out['num'] = pd.to_numeric(df['num'], downcast='integer')

    return df_out.sort_values(by=['time', 'name', 'num'])


def filter_place_changed_events(df):
    '''

    :param df:
    :return:
    '''
    df.sort_values(by=['time'])
    change_frame_list = []
    tstep_set = set()
    for num in df.num.unique():
        for state_name in df.name.unique():
            df_num_name = df[(df.num == num) & (df.name == state_name)]
            df_num_name_changed = df_num_name[df_num_name['count'].diff() != 0]
            # df_num_name_entered = df_num_name_changed[df_num_name_changed['count'] > 0]  # chance will go up > 1
            tstep_set.update(set(df_num_name_changed['tstep']))
            # change_frame_list.append(df_num_name_changed)

    tstep_list = list(tstep_set)
    # tstep_list.sort()

    df_out = df[df['tstep'].isin(tstep_list)]
    # del df_out['count']  # not required for current application and complicates tests
    # df_out['num'] = pd.to_numeric(df_out['num'], downcast='integer')

    return df_out.sort_values(by=['time', 'name', 'num'])


def generate_transition_events(df):
    df = df[df['count'] > 0]
    return df.sort_values(by=['time', 'unit'])


def generate_causal_graph(place_change_events: DataFrame,
                          transition_events: DataFrame,
                          time_per_step: float):
    g = nx.DiGraph()  # Nodes are occasions and edges leading in their prehensions

    # Add the initial state for each node as an occasion with no past
    initial_occasions = place_change_events.query('tstep == 0')
    for occ in initial_occasions.itertuples():
        g.add_node(Occasion(int(occ.num), occ.name, occ.time))  # unit, state, time

    # Visit each transition and identify i) its output node and its 2 input nodes
    for trans in transition_events.itertuples():
        # row has: tstep, time, name, unit, neighbour & count

        # TODO: IS IT SAFE TO IGNORE THIS?
        # assert trans.count == 1  # Statistically likely to happen as simulations get more complex or are undersampled. Consider what to do if this occurs --Rob

        # Create new occasion in graph for this transition
        # output_state = trans.name[1]  # ab -> b
        prefix, input_state, output_state = expand_transition_name(trans.name)  # strings
        if math.isnan(trans.unit):
            print(f"*** {trans.unit} {output_state} {trans.time}")
            continue
        output_occasion = Occasion(int(trans.unit), output_state, trans.time)
        g.add_node(output_occasion)

        def choose_best_upstream_occasion(target_unit, target_state_name, source_time):
            query = f"num=={target_unit} & name=='{target_state_name}' & time<{source_time}"
            last_transition_time = place_change_events.query(query)['time'].max()
            if math.isnan(last_transition_time):
                #  Try including the source time
                query = f"num=={target_unit} & name=='{target_state_name}' & time=={source_time}"
                last_transition_time = place_change_events.query(query)['time'].min()
                if math.isnan(last_transition_time):
                    #  Try including the step after
                    query = f"num=={target_unit} & name=='{target_state_name}' & time<={source_time + time_per_step}"
                    last_transition_time = place_change_events.query(query)['time'].min()
            return Occasion(target_unit, target_state_name, last_transition_time)

        # Determine local input node from same unit
        # state_name = trans.name[0]  # ab -> a
        local_input_occasion = choose_best_upstream_occasion(trans.unit, input_state, trans.time)
        g.add_edge(local_input_occasion, output_occasion)

        # Determine input node from neighbour
        # state_name = trans.name[1]  # ab -> b
        neighbour_input_occasion = choose_best_upstream_occasion(trans.neighbour, output_state, trans.time)
        g.add_edge(neighbour_input_occasion, output_occasion)

        # Determine input node from neighbour2 if set
        if not math.isnan(trans.neighbour2):
            # state_name = trans.name[1]  # ab -> b  # neighbour2 assumed pulling state forward (like neighbour)
            neighbour2_input_occasion = choose_best_upstream_occasion(trans.neighbour2, output_state, trans.time)
            g.add_edge(neighbour2_input_occasion, output_occasion)

    return g


    # def determine_earliest_unused_transition


class Occasion(namedtuple('Occasion', ['unit', 'state', 'time'])):

    def __repr__(self):
        return f"{self.state}{int(self.unit)}@{self.time}"


def extract_state_names_from_causal_graph(causal_graph):
    return set((occasion.state for occasion in causal_graph))


def extract_unit_numbers_from_causal_graph(causal_graph):
    return set((occasion.unit for occasion in causal_graph))


def index_causal_graph_by_state(causal_graph):
    d = defaultdict(list)
    for occasion in causal_graph:
        d[occasion.state].append(occasion)
    return d
