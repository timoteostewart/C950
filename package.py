from collections import namedtuple

Package = namedtuple('Package', ['id', 'street_address', 'zip', 'deadline', 'weight_kg', 'notes', 'when_can_leave_hub', 'package_affinities', 'truck_affinity'])
