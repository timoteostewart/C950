import geo

class Route:

    def __init__(self):
        self.package_manifest = []
        self.manifest_all_packages = []
        self.manifest_required_packages = []
        self.manifest_optional_packages = []

        self.stops_not_yet_added_to_path = []

        self.circuit = []
        self.path_to_farthest = []
        self.path_from_farthest = []

        self.farthest_stop = ''

        self.earliest_bearing = 0.0
        self.latest_bearing = 0.0
        # self.bearing_of_farthest_stop = 0.0

        self.weighted_center = (0.0, 0.0)
        
    def __str__(self) -> str:
        path = ''
        for stop in self.circuit:
            path += f"\'{stop.street_address}\' "
        return path
    
    def update_weighted_center(self):
        self.weighted_center = geo.get_weighted_center_of_stops(self.stops_not_yet_added_to_path)
        self.stops_not_yet_added_to_path.sort(key=lambda stop: geo.haversine_distance(self.weighted_center, stop.lat_long), reverse=True)
        
    def update_farthest_stop(self):
        self.farthest_stop = self.stops_not_yet_added_to_path[0]
        self.path_to_farthest = [geo.HUB_STOP] + [self.farthest_stop]
        self.path_from_farthest = [self.farthest_stop] + [geo.HUB_STOP]
        self.stops_not_yet_added_to_path.remove(self.farthest_stop)    
    