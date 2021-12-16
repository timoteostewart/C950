class Package:
    def __init__(self, id, street_address, zip, deadline_as_offset, weight_kg, notes, when_can_leave_hub, package_affinities, truck_affinity, distance_from_hub):
        self.id = id
        self.street_address: str = street_address
        self.zip: str = zip
        self.deadline_as_offset: int = deadline_as_offset
        self.weight_kg: int = weight_kg
        self.notes: str = notes
        self.when_can_leave_hub_as_offset: int = when_can_leave_hub
        self.package_affinities = package_affinities
        self.truck_affinity: str = truck_affinity # format is: 'truck 1' or 'truck 2'
        self.distance_from_hub: float = distance_from_hub
    
    def __hash__(self) -> int:
        return self.id

    def __str__(self) -> str:
        return f"id {self.id}, lat_long {self.lat_long}"

    def deep_copy(self):
        new_package = Package(self.id, self.street_address, self.zip, self.deadline_as_offset, self.weight_kg, self.notes, self.when_can_leave_hub_as_offset, self.package_affinities, self.truck_affinity, self.distance_from_hub)
        return new_package

