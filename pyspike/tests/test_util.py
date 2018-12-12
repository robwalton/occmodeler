import pyspike.util



def test_generate_state_order_and_colours_with_no_opacity():
    ordered_state_list, color_dict = pyspike.util.generate_state_order_and_colours(['a', 'b', 'c'])

    assert ordered_state_list == ['a', 'b', 'c']
    assert color_dict['a'] == 'rgb(77,175,74)'
    assert color_dict['b'] == 'rgb(55,126,184)'
    assert color_dict['b'] == 'rgb(55,126,184)'


def test_generate_state_order_and_colours_with_opacity():
    ordered_state_list, color_dict = pyspike.util.generate_state_order_and_colours(['a', 'b', 'c'], 0.5)

    assert ordered_state_list == ['a', 'b', 'c']
    assert color_dict['a'] == 'rgba(77,175,74,0.5)'
    assert color_dict['b'] == 'rgba(55,126,184,0.5)'
    assert color_dict['b'] == 'rgba(55,126,184,0.5)'
