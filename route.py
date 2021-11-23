import config
import geo
import my_package
import my_time

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

        self.time_used = 0.0
        self.miles_used = 0.0
        
    def __str__(self) -> str:
        path = f"{len(self.circuit) - 2} stops, {len(self.manifest_all_packages)} packages: "
        for stop in self.circuit:
            path += f"\'{stop.street_address}\' "
        return path


    def add_optional_packages_at_existing_stops(self, nonrush_packages_ready):
        existing_addresses = {x.street_address for x in self.manifest_required_packages}
        for pkg in nonrush_packages_ready:
            if pkg not in self.manifest_all_packages:
                if pkg.street_address in existing_addresses:
                    self.add_optional_package(pkg)
    

    def populate_paths_to_and_from_farthest(self):
        for cur_stop in list(self.stops_not_yet_added_to_path):
            if geo.is_bearing_in_angle(cur_stop.bearing_from_hub, self.earliest_bearing, self.farthest_stop.bearing_from_hub):
                cur_least_distance = float('inf')
                index_insert_after = -1
                for i in range(0, len(self.path_to_farthest) - 1):
                    cur_distance = geo.distance_of_path_of_stops([self.path_to_farthest[i]] + [cur_stop] + [self.path_to_farthest[i+1]])
                    if cur_distance < cur_least_distance:
                        cur_least_distance = cur_distance
                        index_insert_after = i
                self.path_to_farthest.insert(i + 1, cur_stop)
            else:
                cur_least_distance = float('inf')
                index_insert_after = -1
                for i in range(0, len(self.path_from_farthest) - 1):
                    cur_distance = geo.distance_of_path_of_stops([self.path_from_farthest[i]] + [cur_stop] + [self.path_from_farthest[i+1]])
                    if cur_distance < cur_least_distance:
                        cur_least_distance = cur_distance
                        index_insert_after = i
                self.path_from_farthest.insert(i + 1, cur_stop)
            self.stops_not_yet_added_to_path.remove(cur_stop)


    def create_circuit(self):
        self.update_weighted_center()
        self.update_farthest_stop()
        self.populate_paths_to_and_from_farthest()
        self.circuit = self.path_to_farthest + self.path_from_farthest[1:]
        # print(f"circuit length: {geo.distance_of_path_of_stops(self.circuit)}")


    def add_optional_package(self, pkg):
        self.manifest_optional_packages.append(pkg)
        self.combine_manifests_required_optional_packages()


    def add_required_package(self, pkg):
        self.manifest_required_packages.append(pkg)
        self.combine_manifests_required_optional_packages()

    
    def combine_manifests_required_optional_packages(self):
        self.manifest_all_packages = self.manifest_required_packages + self.manifest_optional_packages


    def translate_packages_to_stops(self):
        self.combine_manifests_required_optional_packages()
        for street_address in set([x.street_address for x in self.manifest_all_packages]):
            cur_stop = config.all_stops_by_street_address.get_or_default(street_address, '')
            if cur_stop not in self.stops_not_yet_added_to_path:
                self.stops_not_yet_added_to_path.append(cur_stop)
    
    def update_weighted_center(self):
        self.weighted_center = geo.get_weighted_center_of_stops(self.stops_not_yet_added_to_path)
        # sort stops not yet added in decreasing distance from weighted center
        self.stops_not_yet_added_to_path.sort(key=lambda stop: geo.haversine_distance(self.weighted_center, stop.lat_long), reverse=True)
        
    def update_farthest_stop(self):
        self.farthest_stop = self.stops_not_yet_added_to_path[0]
        self.path_to_farthest = [geo.HUB_STOP] + [self.farthest_stop]
        self.path_from_farthest = [self.farthest_stop] + [geo.HUB_STOP]
        self.stops_not_yet_added_to_path.remove(self.farthest_stop)    
    
    def add_additional_packages_going_to_existing_stops(self):
        existing_addresses = {x.street_address for x in self.manifest_required_packages}
        for pkg in config.pkgs_eight_oclock_all:
            if pkg not in config.eight_oclock_route_1.manifest_required_packages and pkg not in self.manifest_optional_packages:
                if pkg.street_address in existing_addresses:
                    # print(f"pkg id {pkg.id} going to same address as existing package")
                    self.manifest_optional_packages.append(pkg)
        self.manifest_all_packages = self.manifest_required_packages + self.manifest_optional_packages

def populate_two_routes_for_the_given_time(the_time: str):
    
    rush_packages_ready = [x for x in filter(lambda x: x.deadline < 1440 and x.when_can_leave_hub == my_time.convert_time_to_minutes_offset(the_time), config.packages_at_hub)]
    nonrush_packages_ready = [x for x in filter(lambda x: x.deadline == 1440 and x.when_can_leave_hub == my_time.convert_time_to_minutes_offset(the_time), config.packages_at_hub)]

    # 3. create package affinity group
    p_ids_in_affinity = set()
    for pkg in rush_packages_ready:
        if pkg.package_affinities != {0}:
            p_ids_in_affinity.add(pkg.id)
            p_ids_in_affinity.update(pkg.package_affinities)
    for pkg in nonrush_packages_ready:
        if pkg.package_affinities != {0}:
            p_ids_in_affinity.add(pkg.id)
            p_ids_in_affinity.update(pkg.package_affinities)
    affinity_packages_ready = set()
    for p_id in p_ids_in_affinity:
        cur_pkg = config.all_packages_by_id[p_id]
        affinity_packages_ready.add(cur_pkg)
        if cur_pkg in rush_packages_ready:
            rush_packages_ready.remove(cur_pkg)
        if cur_pkg in nonrush_packages_ready:
            nonrush_packages_ready.remove(cur_pkg)
    
    exists_affinity_group = False
    weighted_center_of_affinity_group = None
    if affinity_packages_ready:
        exists_affinity_group = True
        stops = my_package.convert_list_of_packages_to_stops(list(affinity_packages_ready))
        weighted_center_of_affinity_group = geo.get_weighted_center_of_stops(stops)
    # print(weighted_center_of_affinity_group)

    # 4. separate rush packages into two clusters
    rush_packages_ready.sort(key=lambda x: x.bearing_from_hub)
    earliest_bearing = rush_packages_ready[0].bearing_from_hub
    latest_bearing = rush_packages_ready[-1].bearing_from_hub
    list_of_angles = []
    for i, pkg in enumerate(rush_packages_ready):
        cur_bearing = pkg.bearing_from_hub
        next_bearing = -1 # will initialize in if/else block below
        if i + 1 == len(rush_packages_ready):
            next_bearing = rush_packages_ready[0].bearing_from_hub + 360
        else:
            next_bearing = rush_packages_ready[i+1].bearing_from_hub

        cur_diff = abs(next_bearing - cur_bearing)
        list_of_angles.append((cur_diff, cur_bearing, next_bearing))
    list_of_angles.sort(key=lambda x: x[0])
    list_of_angles.reverse()

    # 5. add packages in clusters to routes
    route1 = Route()
    route2 = Route()
    for pkg in rush_packages_ready:
        if geo.is_bearing_in_angle(pkg.bearing_from_hub, list_of_angles[0][2], list_of_angles[1][1]):
            route1.add_required_package(pkg)
        else:
            route2.add_required_package(pkg)

    # 6. add optional packages at existing routes
    route1.add_optional_packages_at_existing_stops(nonrush_packages_ready)
    route2.add_optional_packages_at_existing_stops(nonrush_packages_ready)

    # remove packages on these routes from config.packages_at_hub
    for pkg in route1.manifest_all_packages:
        if pkg in config.packages_at_hub:
            config.packages_at_hub.remove(pkg)
    for pkg in route2.manifest_all_packages:
        if pkg in config.packages_at_hub:
            config.packages_at_hub.remove(pkg)

    route1.translate_packages_to_stops()
    route2.translate_packages_to_stops()
    
    route1.create_circuit()
    route2.create_circuit()
    return (route1, route2)