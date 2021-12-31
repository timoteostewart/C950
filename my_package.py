class Package:
    def __init__(self, id, street_address, city, zip, deadline_as_offset, weight_kg, notes, when_can_leave_hub, package_affinities, truck_affinity, distance_from_hub, delivery_status):
        self.id = id
        self.street_address: str = street_address
        self.city: str = city
        self.zip: str = zip
        self.deadline_as_offset: int = deadline_as_offset
        self.weight_kg: int = weight_kg
        self.notes: str = notes
        self.when_can_leave_hub_as_offset: int = when_can_leave_hub
        self.package_affinities = package_affinities
        self.truck_affinity: str = truck_affinity # format is: 'truck 1' or 'truck 2'
        self.distance_from_hub: float = distance_from_hub
        self.delivery_status = delivery_status


    def __hash__(self) -> int:
        return self.id

