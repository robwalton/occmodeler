import os
import json
import re
from copy import deepcopy
from collections import OrderedDict

OD = OrderedDict


def create_conf_file(model_path, model_args, sim_args, repeat_sim, output_dir):
    """Create a Spike cnfiguration file (.spc)

    :param output_dir:
    :param conf_target_path: Path to write conf file
    :param model_path: Model to import
    :param sim_args: unordered dict of simulation arguments
    :repeat_sim: times to repeat simulation
    :return: list of files which will be written
    """

    sim_args = deepcopy(sim_args)

    if not os.path.isfile(model_path):
        raise Exception("model_path '{}' does not exist.".format(model_path))

    # Make simulation output paths absolute

    export_list = []
    export_path_list = []
    for export_item in sim_args['export']:
        export_item = dict(export_item)
        expanded_path = os.path.join(output_dir, export_item['to'])
        export_item['to'] = expanded_path
        export_list.append(export_item)
        export_path_list.append(expanded_path)
    
    sim_args['export'] = export_list

    od = args_to_od(model_path, model_args, sim_args, repeat_sim)
    spc_string = od_to_spc(od)

    return export_path_list, spc_string


def args_to_od(model_path, model_args, sim_args, repeat_sim=1):
    """
    Create ordered dictionary suitable
    :param model_args:
    :param model_path:
    :param sim_args:
    :return:
    """

    od = OrderedDict()

    # import
    od['import'] = {'from': model_path}

    # configuration
    od['configuration'] = OD()

    # configuration : model
    if model_args:
        od['configuration']['model'] = dict(model_args)  # Assume order unimportant

    # configuration : simulation
    od['configuration']['simulation'] = OD(
        name=sim_args['name'],
        type=sim_args['type'],
        solver=sim_args['solver'],
        threads=sim_args['threads'],
        interval=sim_args['interval'],
        runs=sim_args['runs'],
        export=sim_args['export']
    )

    return od


def _walk(node, f):
    for key in list(node):
        if isinstance(node[key], (dict, OrderedDict)):
            _walk(node[key], f)
        else:
            node[key] = f(node[key])


def od_to_spc(od):

    od = deepcopy(od)

    # ---Prepossess dict---

    # Put ' around certain keys (to later restore with " after all " removed)

    if 'import' in od:
        if 'from' in od['import']:
            od['import']['from'] = "'" + od['import']['from'] + "'"

    if 'configuration' in od:
        if 'model' in od['configuration']:
            _walk(od['configuration']['model'], lambda val: "'" + str(val) + "'")

    if 'configuration' in od:
        if 'simulation' in od['configuration']:
            if 'name' in od['configuration']['simulation']:
                od['configuration']['simulation']['name'] = "'" + od['configuration']['simulation']['name'] + "'"

    # Collapse interval:
    if 'configuration' in od:
        if 'simulation' in od['configuration']:
            if 'interval' in od['configuration']['simulation']:
                interval_dict = od['configuration']['simulation']['interval']
                collapsed = '{start}:{step}:{stop}'.format(**interval_dict)
                od['configuration']['simulation']['interval'] = collapsed

    # Replace export list with export_1, export_2 and so on
    if 'configuration' in od:
        if 'simulation' in od['configuration']:
            if 'export' in od['configuration']['simulation']:
                export_list = od['configuration']['simulation'].pop('export')
                for i, anexport in enumerate(export_list):
                    anexport['to'] = "'" + anexport['to'] + "'"
                    if 'places' in anexport:
                        anexport['places'] = '[' + ', '.join(["'" + p + "'" for p in anexport['places']]) + ']'
                    if 'transitions' in anexport:
                        anexport['transitions'] = '[' + ', '.join(["'" + p + "'" for p in anexport['transitions']]) + ']'
                    od['configuration']['simulation']['export<' + str(i) + '>'] = anexport

    # ---Create and further process json string---

    jrep = json.dumps(od, indent=4)

    # Remove front { and last } and 4 spaces of indent to remainder
    lines = jrep.splitlines()
    lines.pop(0)
    lines.pop(-1)
    for i in range(len(lines)):
        lines[i] = lines[i][4:]
    jrep = '\n'.join(lines)

    # Remove all "
    jrep = jrep.replace('"', '')

    # Remove commas on line ends
    jrep = jrep.replace(',\n', '\n')

    # Replace ' with " (these were placed above)
    jrep = jrep.replace("'", '"')

    # Remove any <#> added during expansion of exports above
    jrep = re.sub('<.>', '', jrep)

    return jrep
