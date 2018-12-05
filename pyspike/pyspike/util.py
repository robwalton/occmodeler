import colorlover as cl


OVERLINE = '\u0304'


def render_name(name):
    return name.lower() + OVERLINE if name.isupper() else name


def generate_state_order_and_colours(state_name_list):
    state_name_list.sort(key=str.lower)

    color_list = cl.scales['9']['qual']['Set1']
    color_list = color_list[:len(state_name_list)]
    color_list.reverse()

    ordered_state_list = state_name_list
    color_dict = {s: c for s, c in zip(state_name_list, color_list)}
    return ordered_state_list, color_dict
