import math

import config

def return_bearing_from_hub_to_street_address(street_address: str) -> float:
    coords = config.street_address_to_lat_long.get_or_default(street_address, '')
    return return_bearing_from_coords1_to_coords2(config.HUB_LAT_LONG, coords)


def return_bearing_from_coords1_to_coords2(coords1, coords2) -> float: # takes coordinates in decimal degrees and returns compass bearing in degrees
    lat1_degrees, long1_degrees = coords1
    lat2_degrees, long2_degrees = coords2

    lat1_radians = math.radians(lat1_degrees)
    lat2_radians = math.radians(lat2_degrees)
    long1_radians = math.radians(long1_degrees)
    long2_radians = math.radians(long2_degrees)

    # bearing calculation was inspired by the information found at https://www.movable-type.co.uk/scripts/latlong.html
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
