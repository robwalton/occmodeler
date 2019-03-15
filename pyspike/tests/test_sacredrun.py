from pprint import pprint

from pyspike.sacred.sacredrun import SacredRun, sacredrun_to_json, json_to_sacredrun

from occ_test_files import RUN_180


def test_sacredrun():
    run = SacredRun(RUN_180)


def test_config():
    run = SacredRun(RUN_180)
    assert run.config['seed'] == 445234732


def test_to_json_and_back():
    run = SacredRun(RUN_180)
    s = sacredrun_to_json(run)
    pprint(s)
    run_decoded = json_to_sacredrun(s)
    assert run_decoded == run

