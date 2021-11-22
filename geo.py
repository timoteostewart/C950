
import math
from collections import namedtuple

import config
from hash_table import HashTable

street_address_to_lat_long = HashTable(27 // config.HASH_TABLE_LOAD_FACTOR)
street_address_to_bearing = HashTable(27 // config.HASH_TABLE_LOAD_FACTOR)

Destination = namedtuple('Destination', ['p_id', 'bearing_from_hub', 'distance_from_hub'])

Stop = namedtuple('Stop', ['street_address', 'lat_long', 'bearing_from_hub', 'distance_from_hub'])



HUB_STOP = Stop(config.HUB_STREET_ADDRESS, config.HUB_LAT_LONG, 0.0, 0.0)

def is_bearing_in_angle(bearing, angle1, angle2):
    if angle2 >= angle1:
        return bearing >= angle1 and bearing <= angle2
    else:
        return bearing >= angle1 or bearing <= angle2


def return_bearing_from_hub_to_street_address(street_address: str) -> float:
    coords = street_address_to_lat_long.get_or_default(street_address, '')
    return return_bearing_from_coords1_to_coords2(config.HUB_LAT_LONG, coords)


def return_bearing_from_coords1_to_coords2(coords1, coords2) -> float: # takes coordinates in decimal degrees and returns compass bearing in degrees
    lat1_degrees, long1_degrees = coords1
    lat2_degrees, long2_degrees = coords2

    lat1_radians = math.radians(lat1_degrees)
    lat2_radians = math.radians(lat2_degrees)
    long1_radians = math.radians(long1_degrees)
    long2_radians = math.radians(long2_degrees)

    # the bearing calculation below was inspired by the information found at https://www.movable-type.co.uk/scripts/latlong.html
    DELTA_LAMBDA = long2_radians - long1_radians
    Y = math.cos(lat1_radians) * math.sin(lat2_radians) - math.sin(lat1_radians) * math.cos(lat2_radians) * math.cos(DELTA_LAMBDA)
    X = math.sin(DELTA_LAMBDA) * math.cos(lat2_radians)
    bearing_radians = math.atan2(Y, X)
    bearing_degrees = math.degrees(bearing_radians)

    # now perform various conversions to translate our degree measurement from math style to compass style
    bearing_degrees *= -1 # translate degrees from math-style counterclockwise orientation to compass-style clockwise orientation
    bearing_degrees += 90 # rotate degrees from math-style "0° means →" to compass-style "0° means ↑"
    bearing_degrees = (bearing_degrees + 360) % 360 # finally, avoid negative degree bearings
    return bearing_degrees


def haversine_distance(coords1, coords2) -> float: # takes coordinates in decimal degrees and returns distance in miles
    # for more information on haversine, see: https://en.wikipedia.org/wiki/Haversine_formula
    lat1_degrees, long1_degrees = coords1
    lat2_degrees, long2_degrees = coords2

    lat1_radians = math.radians(lat1_degrees)
    lat2_radians = math.radians(lat2_degrees)
    long1_radians = math.radians(long1_degrees)
    long2_radians = math.radians(long2_degrees)

    RADIUS_OF_EARTH_meters = 6_370_345 # radius of Earth in meters at Salt Lake City per https://rechneronline.de/earth-radius/
    DELTA_PHI = lat2_radians - lat1_radians
    DELTA_LAMBDA = long2_radians - long1_radians
    A = math.sin(DELTA_PHI / 2) * math.sin(DELTA_PHI / 2) + math.cos(lat1_radians) * math.cos(lat2_radians) * math.sin(DELTA_LAMBDA / 2) * math.sin(DELTA_LAMBDA / 2)
    C = 2 * math.atan2(math.sqrt(A), math.sqrt(1 - A))
    distance_meters = RADIUS_OF_EARTH_meters * C
    distance_miles = distance_meters * 0.000_621_370 # conversion from meters to miles
    return distance_miles


def get_distance(street_address1, street_address2):
    # print(f"{street_address1} and {street_address2}")
    return float(config.distances_between_pairs.get_or_default(f"{street_address1} and {street_address2}", ''))


def get_distance_between_stops(stop1, stop2):
    return get_distance(stop1.street_address, stop2.street_address)


def distance_of_path(list_of_stops):
    distance = 0.0
    if len(list_of_stops) >= 2:
        for i in range(0, len(list_of_stops) - 1):
            distance += get_distance(list_of_stops[i], list_of_stops[i+1])
    return distance


def distance_of_path_of_stops(list_of_stops):
    distance = 0.0
    if len(list_of_stops) >= 2:
        for i in range(0, len(list_of_stops) - 1):
            distance += get_distance_between_stops(list_of_stops[i], list_of_stops[i+1])
    return distance


def get_farthest_stop_from_hub(list_of_stops):
    greatest_distance = 0.0
    farthest_stop = ''
    for stop in list_of_stops:
        cur_distance = get_distance(config.HUB_STREET_ADDRESS, stop)
        if cur_distance > greatest_distance:
            greatest_distance = cur_distance
            farthest_stop = stop
    return farthest_stop


def get_weighted_center_of_stops(list_of_stops) -> tuple[float, float]:
    sum_lat = 0.0
    sum_long = 0.0
    for stop in list_of_stops:
        sum_lat += stop.lat_long[0]
        sum_long += stop.lat_long[1]
    avg_lat = sum_lat / len(list_of_stops)
    avg_long = sum_long / len(list_of_stops)
    return (avg_lat, avg_long)