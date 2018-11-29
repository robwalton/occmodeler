import pandas as pd


def generate_state_change_frame(df):
    df.sort_values(by=['time'])
    change_frame_list = []

    for num in df.num.unique():
        for state_name in df.name.unique():
            df_num_name = df[(df.num == num) & (df.name == state_name)]
            df_num_name_changed = df_num_name[df_num_name['count'].diff() != 0]
            df_num_name_entered = df_num_name_changed[df_num_name_changed['count'] == 1]
            change_frame_list.append(df_num_name_entered)


    # concatenate
    df_out = pd.concat(change_frame_list)
    del df_out['count']
    return df_out.sort_values(by=['num', 'time'])