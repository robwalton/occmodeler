import colorlover as cl
import networkx as nx

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


def check_medium_graph(medium_graph):
    """Assert that g is an nx.Graph having contiguously numbered nodes starting from 0."""

    g = medium_graph
    assert isinstance(g, nx.Graph)
    for node in g.nodes:
        if not isinstance(node, int):
            raise AssertionError(f"node {node} must be of type 'int' not '{type(node)}."
                                 "Use destringizer=int with nx.read_gml()?'")
    assert list(g.nodes)[0] == 0, f"medium_graph nodes must be numbered from 0 not {list(g.nodes)[0]}"
    assert list(g.nodes) == list(range(len(g.nodes)))
