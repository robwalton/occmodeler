import urllib
from pathlib import Path

import plotly.offline as pl

if __name__ == "__main__":
    import sys
    sys.path.insert(0, 'src/pyspike')


from pyspike.sacred.spike_ingredient import prep_for_spike_call, call_spike
from pyspike.sacred.candl_ingredient import generate_candl_file
from pyspike.sacred.visualisation_ingredient import visualise_temporal_graph, visualise_network_animation
from occ.vis.analysis import generate_sums_by_state_figure


def main(ex, candl, spike, visualisation, log, run_id):

    if candl['candl_template_path']:
        assert not spike['model_path']
        assert candl['gml_path']
        if 'medium_gml_path' in visualisation:
            assert visualisation['medium_gml_path'] == candl['gml_path']
        else:
            visualisation['medium_gml_path'] = candl['gml_path']
        use_generated_candl = True
    else:
        assert spike['model_path']
        assert not candl['gml_path']
        assert visualisation['medium_gml_path']

        use_generated_candl = False

    # Generate candl file if requested
    if use_generated_candl:
        resource_path_list, generate_candl_path = generate_candl_file()
        _add_resources(ex, resource_path_list, log)

    # Prep for Spike call
    if use_generated_candl:
        resource_path_list, artifact_path_list = prep_for_spike_call(model_path=generate_candl_path)
    else:
        resource_path_list, artifact_path_list = prep_for_spike_call()

    _add_resources(ex, resource_path_list, log)

    # Call Spike
    call_spike()

    # Add artifacts
    for path in artifact_path_list:
        if not Path(path).exists():
            raise Exception(f"Expected artifact '{path}' does not exist. Did Spike fail?")
    _add_artifacts(ex, artifact_path_list, log)  # Can this be done earlier?

    # Visualise

    places_path = Path('_spike/output/places.csv')
    transitions_path = Path('_spike/output/transitions.csv')

    # Check ingredients are all configured appropriately
    assert str(places_path) in artifact_path_list
    assert str(transitions_path) in artifact_path_list
    gml_path = visualisation['medium_gml_path']
    assert gml_path
    plot_path_list = _show_plots(gml_path, places_path, transitions_path,
                                 spike['sim_args']['runs'], log, run_id)
    _add_artifacts(ex, plot_path_list, log)

    # Wrap up
    log.info('Run ID: ' + str(run_id))


def _add_resources(ex, resource_path_list, _log):
    for resource in resource_path_list:
        _log.info(f'Resource: {resource}')
        ex.add_resource(resource)


def _add_artifacts(ex, artifact_path_list, _log):
    for artifact in artifact_path_list:
        _log.info(f'Artifact: {artifact}')
        ex.add_artifact(artifact)


def visualise(candl, spike, _log, run_num=None):
    if run_num is None:
        _log.info(
            f"Running command 'visualise' with current config and last _spike/output "
            "Ensure these are compatible!")
        places_path = Path('_spike/output/places.csv')
        transitions_path = Path('_spike/output/transitions.csv')
        assert candl['gml_path']
        assert spike['sim_args']['runs'] == 1
    else:
        _log.info(f"Running command 'visualise' on saved run {run_num}")
        runs = Path(f'runs/{run_num}/')
        places_path = runs / 'places.csv'
        transitions_path = runs / 'transitions.csv'
    num_runs = 1  # TODO: should read from config!
    _show_plots(candl['gml_path'], places_path, transitions_path, num_runs, _log, run_num)


def _show_plots(gml_path, places_path, transitions_path, num_runs, log, run_id):
    jupyter_inline = False
    plot_func = pl.iplot if jupyter_inline else pl.plot

    plot_path_list = []

    if num_runs == 1:
        log.info('* Visualising temporal network *')
        fig = visualise_temporal_graph(
            places_path, transitions_path, Path(gml_path), run_id=run_id)
        plot_url = plot_func(fig, filename='causal_graph.html')
        plot_path = urllib.parse.urlparse(plot_url).path
        log.info(f'Causal graph: {plot_path}')
        plot_path_list.append(plot_path)
    else:
        log.info(f"* Skipping temporal network as runs > 1 ({num_runs})*")

    log.info('* Visualising network animation with slider *')
    fig = visualise_network_animation(
        places_path, Path(gml_path), num_runs, run_id=run_id)
    plot_url = plot_func(fig, filename='network_animation_with_slider.html')
    plot_path = urllib.parse.urlparse(plot_url).path
    log.info(f'Animation: {plot_path}')
    plot_path_list.append(plot_path)

    log.info('Plotting counts by time')
    fig = generate_sums_by_state_figure(places_path, run_id=run_id)
    plot_url = plot_func(fig, filename='Non-coloured-counts.html')
    plot_path = urllib.parse.urlparse(plot_url).path
    log.info(f'Non-coloured counts path: {plot_path}')
    plot_path_list.append(plot_path)

    return plot_path_list
