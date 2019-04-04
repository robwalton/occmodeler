import colorlover as cl

OVERLINE = '\u0304'


def render_name(name):
    return name.lower() + OVERLINE if name.isupper() else name


def generate_state_order_and_colours(state_name_list, opacity=None):
    state_name_list.sort(key=str.lower)

    color_list = cl.scales['9']['qual']['Set1']
    color_list = color_list[:len(state_name_list)]
    color_list.reverse()

    if opacity:
        final_color_list = scales_to_rgba_strings_with_opacity(color_list, opacity)
    else:
        final_color_list = color_list

    ordered_state_list = state_name_list
    color_dict = {s: c for s, c in zip(state_name_list, final_color_list)}

    return ordered_state_list, color_dict


def scales_to_rgba_strings_with_opacity(scale, opacity):
    rgb_tuple_list = cl.to_numeric(scale)
    rgba_str_list = []
    for r, g, b in rgb_tuple_list:
        rgba_str_list.append(f'rgba({int(r)},{int(g)},{int(b)},{opacity})')
    return rgba_str_list


