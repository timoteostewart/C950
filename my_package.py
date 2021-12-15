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
        self.when_can_leave_hub_as_offset: int = when_can_leave_hub
        self.package_affinities = package_affinities
        self.truck_affinity: str = truck_affinity # format is: 'truck 1' or 'truck 2'
        self.lat_long = lat_long
        self.bearing_from_hub: float = bearing_from_hub
        self.distance_from_hub: float = distance_from_hub
    
    def __hash__(self) -> int:
        return self.id

    
    def __str__(self) -> str:
        return f"id {self.id}, lat_long {self.lat_long}"

    def deep_copy(self):
        new_package = Package(self.id, self.street_address, self.zip, self.deadline_as_offset, self.weight_kg, self.notes, self.when_can_leave_hub_as_offset, self.package_affinities, self.truck_affinity, self.lat_long, self.bearing_from_hub, self.distance_from_hub)
        return new_package

