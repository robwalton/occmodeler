
from pathlib import Path

FILE_IN_ASSETS = Path(__file__).parents[0] / 'assets' / 'touch_me_to_cause_dash_reload_while_in_dev_mode'


def reload_dash_server():
    # See https://community.plot.ly/t/live-update-by-pushing-from-server-rather-than-polling-or-hitting-reload
    FILE_IN_ASSETS.touch()

# NOTE: probably not a good idea to start from within python as no terminal output and process ownership muddle
# def start_redis():
#     pass
#
# def stop_redis():
#     pass


# def start_dash_server():
#     pass
#
#
# def kill_all_dash_servers():
#     pass



