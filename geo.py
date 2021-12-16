from collections import namedtuple

import config

Stop = namedtuple('Stop', ['street_address', 'distance_from_hub'])

HUB_STREET_ADDRESS = '4001 S 700 East'
HUB_STOP = Stop(HUB_STREET_ADDRESS, 0.0)

def get_distance(street_address1, street_address2):
    return float(config.distances_between_pairs.get(f"{street_address1} and {street_address2}"))

def get_distance_between_stops(stop1, stop2):
    return get_distance(stop1.street_address, stop2.street_address)
