import os
import pathlib
import sys


def add_pyspike_to_path():
    _add_to_path_if_necessary('pyspike')


def add_occdash_to_path():
    _add_to_path_if_necessary('occdash')


def _add_to_path_if_necessary(package: str):
    package_dir = str(pathlib.Path(os.path.abspath('')).parents[0] / package)
    if package_dir not in sys.path:
        sys.path.insert(0, package_dir)
        print(f"Added to python path: '{package_dir}'")
    else:
        print(f"'{package}' already on python path!")
