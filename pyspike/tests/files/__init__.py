
import os.path
from pathlib import Path

THIS_DIR = os.path.dirname(os.path.realpath(__file__))
TEMPORAL = os.path.join(THIS_DIR, 'temporal')
PLACES = os.path.join(TEMPORAL, 'places.csv')
TRANSITIONS = os.path.join(TEMPORAL, 'transitions.csv')

RUN_71_PLACES = os.path.join(THIS_DIR, 'run_71', 'places.csv')
RUN_71_TRANSITIONS = os.path.join(THIS_DIR, 'run_71', 'transitions.csv')
RUN_71_NETWORK_GML = os.path.join(THIS_DIR, 'run_71', 'network.gml')

SPIKERUN_GML = os.path.join(THIS_DIR, 'spikerun', '2x2-hex-lattice.gml')
SPIKERUN_CANDL_TEMPLATE = os.path.join(THIS_DIR, 'spikerun', 'last-registered.template.candl')

MONTE_CARLO_TOS_10000 = os.path.join(THIS_DIR, 'places-tos-net-10000-monte-carlo.csv')

RUN_90 = Path(__file__).parent / 'run_90_are_both_neighbours'
RUN_90_PLACES = RUN_90 / 'places.csv'
RUN_90_TRANSITIONS = RUN_90 / 'transitions.csv'
RUN_90_GML = RUN_90 / '3-triangle-truss.gml'
