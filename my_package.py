from collections import namedtuple
from math import dist

import config
import my_time


class Package:

    # Package(package_id, street_address, zip, deadline, weight_kg, notes, when_can_leave_hub, package_affinities, truck_affinity, lat_long, bearing_from_hub, distance_from_hub)
    def __init__(self, id, street_address, zip, deadline_as_offset, weight_kg, notes, when_can_leave_hub, package_affinities, truck_affinity, lat_long, bearing_from_hub, distance_from_hub):
        self.id = id
        self.street_address: str = street_address
        self.zip: str = zip
        self.deadline_as_offset: int = deadline_as_offset
        self.weight_kg: int = weight_kg
        self.notes: str = notes
        self.when_can_leave_hub: int = when_can_leave_hub
        self.package_affinities = package_affinities
        self.truck_affinity: str = truck_affinity
        self.lat_long = lat_long
        self.bearing_from_hub: float = bearing_from_hub
        self.distance_from_hub: float = distance_from_hub
    
    def __hash__(self) -> int:
        return self.id

    
    def __str__(self) -> str:
        return f"id {self.id}, lat_long {self.lat_long}"


def retrieve_package_ids_able_to_leave_hub(time):
    offset = my_time.convert_time_to_minutes_offset(time)
    return [p_id for p_id in config.packages_at_hub if config.all_packages_by_id[p_id].when_can_leave_hub <= offset]


def convert_list_of_packages_to_stops(list_of_packages):
    street_addresses = list(set([x.street_address for x in list_of_packages]))
    stops = [config.all_stops_by_street_address.get(x) for x in street_addresses]
    return(stops)
