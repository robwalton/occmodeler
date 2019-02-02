import os
import json
import re
from copy import deepcopy
from collections import OrderedDict

OD = OrderedDict


def create_conf_file(model_path, model_args, sim_args, repeat_sim, output_dir):
    """Create a Spike cnfiguration file (.spc)

    :param model_args:
    :param repeat_sim:
    :return:
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
    spc_string = od_to_spc(od, repeat_sim)

    if repeat_sim > 1:
        export_path_list = expand_export_path_list(export_path_list, repeat_sim)
    return export_path_list, spc_string


def expand_export_path_list(export_path_list, repeat_sim):
    expanded_path_list = []
    for path in export_path_list:
        expanded_path_list.append(path)
        for i in range(repeat_sim):
            expanded_path_list.append(path.replace('.csv', f"_{i:04d}.csv"))
    return expanded_path_list


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


    # TODO: remove repeated code

    # NOTE: Even when repeat_sim > 1 write an un-numbered file too. This means that if 10 sims are asked for the code
    # will run 11, but meas the existing pipelin will work as is. TODO: Fix pipeline to run with numbered files.

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
    if repeat_sim > 1:
        assert repeat_sim <= 10000  # we will hard code the number of digits to 4 (but start at 0)
        for i in range(repeat_sim):
            export_dict_list = deepcopy(sim_args['export'])
            export_dict_list = add_repeat_sim_index_export_dict_list(export_dict_list, i)
            od['configuration'][sim_key(i)] = OD(
                name=sim_args['name'],
                type=sim_args['type'],
                solver=sim_args['solver'],
                threads=sim_args['threads'],
                interval=sim_args['interval'],
                runs=sim_args['runs'],
                export=export_dict_list
            )

    return od

def add_repeat_sim_index_export_dict_list(edl, i):
    numbered_edl = []
    for d in edl:
        d_numbered = deepcopy(d)
        d_numbered['to'] = d_numbered['to'].replace('.csv', f"_{i:04d}.csv")
        numbered_edl.append(d_numbered)
    return numbered_edl


def sim_key(sim_index):
    return "<{:04d}>simulation".format(sim_index)

def _walk(node, f):
    for key in list(node):
        if isinstance(node[key], (dict, OrderedDict)):
            _walk(node[key], f)
        else:
            node[key] = f(node[key])


def od_to_spc(od, repeat_sim):

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
        if repeat_sim > 1:
            for i in range(repeat_sim):
                if sim_key(i) in od['configuration']:
                    if 'name' in od['configuration'][sim_key(i)]:
                        od['configuration'][sim_key(i)]['name'] = "'" + od['configuration'][sim_key(i)][
                            'name'] + "'"

    # Collapse interval:

    def collapse_interval(sk):
        if 'interval' in od['configuration'][sk]:
            interval_dict = od['configuration'][sk]['interval']
            collapsed = '{start}:{step}:{stop}'.format(**interval_dict)
            od['configuration'][sk]['interval'] = collapsed

    if 'configuration' in od:
        if 'simulation' in od['configuration']:
            collapse_interval('simulation')
        if repeat_sim > 1:
            for i in range(repeat_sim):
                collapse_interval(sim_key(i))




    # Replace export list with export_1, export_2 and so on
    def expand_export_list(sk):
        if 'export' in od['configuration'][sk]:
            export_list = od['configuration'][sk].pop('export')
            for i, anexport in enumerate(export_list):
                anexport['to'] = "'" + anexport['to'] + "'"
                if 'places' in anexport:
                    anexport['places'] = '[' + ', '.join(["'" + p + "'" for p in anexport['places']]) + ']'
                if 'transitions' in anexport:
                    anexport['transitions'] = '[' + ', '.join(["'" + p + "'" for p in anexport['transitions']]) + ']'
                od['configuration'][sk]['export<' + str(i) + '>'] = anexport

    if 'configuration' in od:
        if 'simulation' in od['configuration']:
            expand_export_list('simulation')
        if repeat_sim > 1:
            for ri in range(repeat_sim):
                expand_export_list(sim_key(ri))


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
    jrep = re.sub('<.+>', '', jrep)

    return jrep
