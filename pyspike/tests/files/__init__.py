
import os.path

THIS_DIR = os.path.dirname(os.path.realpath(__file__))
TEMPORAL = os.path.join(THIS_DIR, 'temporal')
PLACES = os.path.join(TEMPORAL, 'places.csv')
TRANSITIONS = os.path.join(TEMPORAL, 'transitions.csv')