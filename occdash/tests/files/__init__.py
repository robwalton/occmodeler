
import os.path
from pathlib import Path



RUN_180 = Path(__file__).parent / 'run_180'
RUN_90_PLACES = RUN_90 / 'places.csv'
RUN_90_TRANSITIONS = RUN_90 / 'transitions.csv'
RUN_90_GML = RUN_90 / '3-triangle-truss.gml'

# Last registered both single and two neighbour following on tos network
RUN_100 = Path(__file__).parent / 'run_100'
RUN_100_PLACES = RUN_100 / 'places.csv'
RUN_100_TRANSITIONS = RUN_100 / 'transitions.csv'
RUN_100_GML = RUN_100 / 'tos-network.gml'
