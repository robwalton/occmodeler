import json
from pathlib import Path


class SacredRun:

    def __init__(self, root_run_path: Path):
        assert root_run_path.exists()
        assert root_run_path.is_dir()
        self.run_path = root_run_path
        self.config_path = root_run_path / 'config.json'
        self.cout_path = root_run_path / 'cout.txt'
        self.metric_path = root_run_path / 'metric.json'
        self.places_path = root_run_path / 'places.csv'
        self.run_path = root_run_path / 'run.csv'
        self.transitions_path = root_run_path / 'transitions.csv'
        self.medium_graph = root_run_path / 'medium_graph.gml'

    @property
    def config(self):
        with open(self.config_path) as f:
            return json.load(f)



    # places = tidydata.read_csv(filename=str(places_path), node_type="place", drop_non_coloured_sums=True)
    # transitions = tidydata.read_csv(filename=str(transitions_path), node_type="transition", drop_non_coloured_sums=True)
    # _, _, tstep = tidydata.determine_time_range_of_data_frame(places)
    # places = pyspike.tidydata.prepend_tidy_frame_with_tstep(places)
    # transitions = pyspike.tidydata.prepend_tidy_frame_with_tstep(transitions)
    #
    # place_change_events = pyspike.temporal.generate_place_change_events(places)
    # transition_events = pyspike.temporal.generate_transition_events(transitions)
    #
    # causal_graph = pyspike.temporal.generate_causal_graph(
    #     place_change_events, transition_events, time_per_step=tstep)
