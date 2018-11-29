import os

import networkx as nx
from sacred import Ingredient

from pyspike.petrinet import generate_candl_file_from_template
from pyspike.sacred import TMP_SPIKE_INPUT_CANDL_PATH

candl_ingredient = Ingredient('candl')


@candl_ingredient.config
def candl_config():
    candl_template_path = ''
    gml_path = 'blank.gml'


@candl_ingredient.capture
def generate_candl_file(candl_template_path, gml_path):

    assert os.path.isfile(gml_path)
    graph = nx.read_gml(gml_path, destringizer=int)

    _remove_file_if_exist(TMP_SPIKE_INPUT_CANDL_PATH)

    with open(candl_template_path, 'r') as f:
        candl_file_template_text = f.read()

    candl_file_text = generate_candl_file_from_template(candl_file_template_text, graph)

    with open(TMP_SPIKE_INPUT_CANDL_PATH, 'w') as f:
        f.write(candl_file_text)

    resource_path_list = [candl_template_path, gml_path, TMP_SPIKE_INPUT_CANDL_PATH]
    candl_model_path = TMP_SPIKE_INPUT_CANDL_PATH
    return resource_path_list, candl_model_path


def _remove_file_if_exist(path):
    try:
        os.remove(path)
    except FileNotFoundError:
        pass
