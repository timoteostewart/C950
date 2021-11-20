from collections import namedtuple

import config
import my_time

Package = namedtuple('Package', ['id', 'street_address', 'zip', 'deadline', 'weight_kg', 'notes', 'when_can_leave_hub', 'package_affinities', 'truck_affinity', 'lat_long', 'bearing_from_hub', 'distance_from_hub'])

def retrieve_packages_ready_to_go(time):
    offset = my_time.convert_time_to_minutes_offset(time)
    return [p_id for p_id in config.hub_package_list if config.all_packages_by_id[p_id].when_can_leave_hub <= offset]
