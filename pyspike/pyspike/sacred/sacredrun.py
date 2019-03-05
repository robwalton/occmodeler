import json
from pathlib import Path


class SacredRun:

    def __init__(self, root_run_path: Path):
        assert root_run_path.exists()
        assert root_run_path.is_dir()
        self.root_run_path_string = str(root_run_path)

    def __eq__(self, other):
        return self.root_run_path_string == other.root_run_path_string

    # Paths

    @property
    def root_path(self):
        return Path(self.root_run_path_string)

    @property
    def config_path(self):
        return self.root_path / 'config.json'

    @property
    def places_path(self):
        return self.root_path / 'places.csv'

    @property
    def run_path(self):
        return self.root_path / 'run.csv'

    @property
    def transitions_path(self):
        return self.root_path / 'transitions.csv'

    @property
    def medium_graph_path(self):
        return self.root_path / 'medium_graph.gml'

    # requiring file access the following could be cached too

    @property
    def config(self):
        with open(self.config_path) as f:
            return json.load(f)

    # TODO: consider putting medium_graph on here


def _encode_sacredrun(obj):
    if isinstance(obj, SacredRun):
        return dict(__sacredrun__=True, root_path_string=obj.root_run_path_string)
    else:
        type_name = obj.__class__.__name__
        raise TypeError(f"Object of type '{type_name}' is not JSON serializable")


def _decode_sacredrun(dct):
    if "__sacredrun__" in dct:
        return SacredRun(Path(dct["root_path_string"]))
    return dct


def sacredrun_to_json(run):
    return json.dumps(run, default=_encode_sacredrun)


def json_to_sacredrun(data):
    return json.loads(data, object_hook=_decode_sacredrun)
