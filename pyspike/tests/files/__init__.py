
import os.path

THIS_DIR = os.path.dirname(os.path.realpath(__file__))
TEMPORAL = os.path.join(THIS_DIR, 'temporal')
PLACES = os.path.join(TEMPORAL, 'places.csv')
TRANSITIONS = os.path.join(TEMPORAL, 'transitions.csv')

RUN_71_PLACES = os.path.join(THIS_DIR, 'run_71', 'places.csv')
RUN_71_TRANSITIONS = os.path.join(THIS_DIR, 'run_71', 'transitions.csv')
RUN_71_NETWORK_GML = os.path.join(THIS_DIR, 'run_71', 'network.gml')

SPIKERUN_GML = os.path.join(THIS_DIR, 'spikerun', '2x2-hex-lattice.gml')
SPIKERUN_CANDL_TEMPLATE = os.path.join(THIS_DIR, 'spikerun', 'last-registered.template.candl')
