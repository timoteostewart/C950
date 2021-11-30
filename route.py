import math

import config
import geo
import my_package
import my_time

class Route:

    def __init__(self, name):
        self.name = name
        self.truck_number = 0

        self.package_manifest = []
        self.manifest_all_packages = []
        self.manifest_required_packages = []
        self.manifest_optional_packages = []

        self.stops_not_yet_added_to_path = []

        self.circuit = []
        self.path_to_farthest = []
        self.path_from_farthest = []

        self.farthest_stop = None

        self.earliest_bearing = 0.0
        self.latest_bearing = 0.0

        self.weighted_center = (0.0, 0.0)

        self.time_used = 0.0
        self.miles_used = 0.0
        
    def __str__(self) -> str:
        path = f"{len(self.circuit) - 2} stops, {len(self.manifest_all_packages)} packages: "
        for stop in self.circuit:
            path += f"\'{stop.street_address}\' "
        return path

    def massage_stops_into_better_order_if_possible(self):
        # TODO
        pass

    def add_optional_packages_at_existing_stops(self, nonrush_packages_ready):
        existing_addresses = {x.street_address for x in self.manifest_required_packages}
        for pkg in nonrush_packages_ready:
            if pkg not in self.manifest_all_packages:
                if pkg.street_address in existing_addresses:
                    self.add_optional_package(pkg)

    def update_route_bearings_per_new_package(self, pkg):
        if not geo.is_bearing_in_angle(pkg.bearing_from_hub, self.earliest_bearing, self.latest_bearing):
            if geo.get_angle(self.latest_bearing, pkg.bearing_from_hub) < geo.get_angle(pkg.bearing_from_hub, self.earliest_bearing):
                self.latest_bearing = pkg.bearing_from_hub
            else:
                self.earliest_bearing = pkg.bearing_from_hub
        # if self.farthest_stop is not None:
        #     if pkg.distance_from_hub > self.farthest_stop.distance_from_hub:
        #         self.farthest_stop = config.all_stops_by_street_address.get(pkg.street_address)

    def add_required_package(self, pkg):
        if pkg not in self.manifest_required_packages:
            self.update_route_bearings_per_new_package(pkg)
            self.manifest_required_packages.append(pkg)
            if pkg in config.packages_at_hub:
                config.packages_at_hub.remove(pkg)
            self.combine_manifests_required_optional_packages()

    def add_optional_package(self, pkg):
        if pkg not in self.manifest_optional_packages:
            self.update_route_bearings_per_new_package(pkg)
            self.manifest_optional_packages.append(pkg)
            config.packages_at_hub.remove(pkg)
            self.combine_manifests_required_optional_packages()
    
    def combine_manifests_required_optional_packages(self):
        self.manifest_all_packages = self.manifest_required_packages + self.manifest_optional_packages

    def populate_paths_to_and_from_farthest(self):

        # translate packages into stops
        for street_address in set([x.street_address for x in self.manifest_all_packages]):
            cur_stop = config.all_stops_by_street_address.get(street_address)
            if cur_stop not in self.stops_not_yet_added_to_path:
                self.stops_not_yet_added_to_path.append(cur_stop)

        # sort stops in descending distance from weighted center
        self.weighted_center = geo.get_weighted_center_of_objects(self.stops_not_yet_added_to_path)
        self.stops_not_yet_added_to_path.sort(key=lambda stop: geo.haversine_distance(geo.HUB_LAT_LONG, stop.lat_long), reverse=True)
        self.farthest_stop = self.stops_not_yet_added_to_path[0]

        self.path_to_farthest = [geo.HUB_STOP] + [self.farthest_stop]
        self.path_from_farthest = [self.farthest_stop] + [geo.HUB_STOP]
        self.stops_not_yet_added_to_path.remove(self.farthest_stop)
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
        self.populate_paths_to_and_from_farthest()
        self.circuit = self.path_to_farthest + self.path_from_farthest[1:]

    def convert_circuit_to_package_delivery_order(self):
        for stop in self.circuit:
            for pkg in self.manifest_all_packages:
                if pkg.street_address == stop.street_address:
                    print(f"{pkg.id} ", end='')
        print()


def validate_route(a_route, departure_time, reverse):
    cur_time_as_offset = my_time.convert_time_to_minutes_offset(departure_time)
    packages_to_deliver = list(a_route.manifest_all_packages)
    packages_delivered = []
    at_least_one_package_delivered_late = False

    the_circuit = a_route.circuit
    if reverse == True:
        the_circuit.reverse()

    print(f"leaving hub at {my_time.convert_minutes_offset_to_time(cur_time_as_offset)}")

    for i, stop in enumerate(the_circuit):
        if i + 1 == len(the_circuit):
            break
        prev_stop = stop
        cur_stop = the_circuit[i+1]
        leg_distance = geo.get_distance_between_stops(prev_stop, cur_stop)
        leg_time = leg_distance * config.MINUTES_PER_MILE
        cur_time_as_offset = int(math.ceil(cur_time_as_offset + leg_time)) # round time up to next minute

        print(f"arriving at {cur_stop.street_address} at {my_time.convert_minutes_offset_to_time(cur_time_as_offset)}")

        packages_delivered_this_stop = []
        for pkg in packages_to_deliver:
            if pkg.street_address == cur_stop.street_address:
                packages_delivered_this_stop.append(pkg)
                packages_delivered.append(pkg)
                if pkg.deadline_as_offset < 1440:
                    if pkg.deadline_as_offset < cur_time_as_offset:
                        at_least_one_package_delivered_late = True
                        print(f"    rush pkg with id {pkg.id} delivered late at {my_time.convert_minutes_offset_to_time(cur_time_as_offset)} (due at {my_time.convert_minutes_offset_to_time(pkg.deadline_as_offset)})")
                    else:
                        print(f"    rush pkg with id {pkg.id} delivered in time at {my_time.convert_minutes_offset_to_time(cur_time_as_offset)} (due at {my_time.convert_minutes_offset_to_time(pkg.deadline_as_offset)})")
                else:
                    print(f"         pkg with id {pkg.id} delivered at {my_time.convert_minutes_offset_to_time(cur_time_as_offset)}")
        for pkg in packages_delivered_this_stop:
            packages_to_deliver.remove(pkg)
    
    total_mileage = cur_time_as_offset * config.MILES_PER_MINUTE
    miles_per_package = total_mileage / len(packages_delivered)
    print(f"back to hub at {my_time.convert_minutes_offset_to_time(cur_time_as_offset)}")
    return (not at_least_one_package_delivered_late, total_mileage, miles_per_package)


def populate_one_route_for_the_given_time(the_time: str):
    # TODO
    pass

def get_angles_between_packages_sorted_greatest_to_least(list_of_packages):
    list_of_packages.sort(key=lambda pkg: pkg.bearing_from_hub)
    list_of_angles = []
    for i, pkg in enumerate(list_of_packages):
        cur_bearing = pkg.bearing_from_hub
        next_bearing = None # will initialize in if/else block below
        if i + 1 == len(list_of_packages):
            next_bearing = list_of_packages[0].bearing_from_hub + 360
        else:
            next_bearing = list_of_packages[i+1].bearing_from_hub

        cur_diff = next_bearing - cur_bearing
        list_of_angles.append((cur_diff, cur_bearing, next_bearing))
    list_of_angles.sort(key=lambda x: x[0])
    list_of_angles.reverse()
    return list_of_angles


def populate_two_routes_for_the_given_time(the_time: str):
    
    rush_packages_ready = [x for x in filter(lambda x: x.deadline_as_offset < 1440 and x.when_can_leave_hub == my_time.convert_time_to_minutes_offset(the_time), config.packages_at_hub)]
    
    nonrush_packages_ready = [x for x in filter(lambda x: x.deadline_as_offset == 1440 and x.when_can_leave_hub == my_time.convert_time_to_minutes_offset(the_time), config.packages_at_hub)]

    seed_packages = []
    if rush_packages_ready:
        seed_packages += rush_packages_ready
    else:
        seed_packages += nonrush_packages_ready

    # 3.1 create package affinity group
    p_ids_in_affinity = set()
    for pkg in rush_packages_ready:
        if pkg.package_affinities != {0}:
            p_ids_in_affinity.add(pkg.id)
            p_ids_in_affinity.update(pkg.package_affinities)
    for pkg in nonrush_packages_ready:
        if pkg.package_affinities != {0}:
            p_ids_in_affinity.add(pkg.id)
            p_ids_in_affinity.update(pkg.package_affinities)
    affinity_packages_ready = []
    for p_id in p_ids_in_affinity:
        cur_pkg = config.all_packages_by_id[p_id]
        affinity_packages_ready.append(cur_pkg)
        if cur_pkg in config.packages_at_hub:
            config.packages_at_hub.remove(cur_pkg)
        if cur_pkg in rush_packages_ready:
            rush_packages_ready.remove(cur_pkg)
        if cur_pkg in nonrush_packages_ready:
            nonrush_packages_ready.remove(cur_pkg)
        if cur_pkg in seed_packages:
            seed_packages.remove(cur_pkg)

    # if any affinity packages are in seed_packages, then all affinity packages must be added to seed_packages
    exists_package_affinity_group = False
    affinity_packages_weighted_center = None
    if affinity_packages_ready:
        exists_package_affinity_group = True
        # calculate weighted center of affinity package stops
        stops = my_package.convert_list_of_packages_to_stops(affinity_packages_ready)
        affinity_packages_weighted_center = geo.get_weighted_center_of_objects(stops)
        # determine whether to add affinity packages to seed packages
        add_affinity_packages_to_seed = False
        for aff_pkg in affinity_packages_ready:
            if aff_pkg in seed_packages:
                add_affinity_packages_to_seed = True
                break
    
    # # 3.2 create truck affinity group
    # TODO
    # affinity_truck_ready = []
    # for pkg in rush_packages_ready:
    #     if pkg.truck_affinity != 0:
    #         affinity_truck_ready.add(pkg)
    #         rush_packages_ready.remove(pkg)
    # for pkg in nonrush_packages_ready:
    #     if pkg.truck_affinity != 0:
    #         affinity_truck_ready.append(pkg)
    #         nonrush_packages_ready.remove(pkg)
    # exists_truck_affinity_group = affinity_truck_ready

    # 4. divide seed packages into two sectors
    list_of_angles = get_angles_between_packages_sorted_greatest_to_least(seed_packages)

    # 5. add seed packages to routes according to sector

    route1 = Route('route1')
    route2 = Route('route2')
    route1.earliest_bearing = list_of_angles[0][2]
    route1.latest_bearing = list_of_angles[1][1]
    route2.earliest_bearing = list_of_angles[1][2]
    route2.latest_bearing = list_of_angles[0][1]
    for pkg in seed_packages:
        if geo.is_bearing_in_angle(pkg.bearing_from_hub, list_of_angles[0][2], list_of_angles[1][1]):
            route1.add_required_package(pkg)
        else:
            route2.add_required_package(pkg)

    # 6. add optional packages at existing stops
    # TODO: change this to add them in decreasing order of distance from hub
    route1.add_optional_packages_at_existing_stops(nonrush_packages_ready)
    route2.add_optional_packages_at_existing_stops(nonrush_packages_ready)

    # 7. add affinity group to route best suited for it, and move stops (and packages) from one route to other as needed to avoid going over package limit
    route1_weighted_center = geo.get_weighted_center_of_objects(route1.manifest_all_packages)
    route2_weighted_center = geo.get_weighted_center_of_objects(route2.manifest_all_packages)
    if geo.haversine_distance(affinity_packages_weighted_center, route1_weighted_center) < geo.haversine_distance(affinity_packages_weighted_center, route2_weighted_center):
        for pkg in affinity_packages_ready:
            route1.add_required_package(pkg)
    else:
        for pkg in affinity_packages_ready:
            route2.add_required_package(pkg)

    # 8. validate if either route has too many packages
    # only packages added should be: rush + same_stop_non_rush + package affinity
    if len(route1.manifest_all_packages) > 16:
        overload = len(route1.manifest_all_packages) - 16
        # find the n packages closest to the hub and remove them from the manifest
        route1.manifest_optional_packages.sort(key=lambda pkg: geo.haversine_distance(geo.HUB_LAT_LONG, pkg.lat_long))
        for i in range(0, min(overload, len(route1.manifest_optional_packages))):
            cur_pkg = route1.manifest_optional_packages[0]
            config.packages_at_hub.append(cur_pkg)
            route1.manifest_optional_packages.remove(cur_pkg)
    if len(route2.manifest_all_packages) > 16:
        overload = len(route2.manifest_all_packages) - 16
        # find the n packages closest to the hub and remove them from the manifest
        route2.manifest_optional_packages.sort(key=lambda pkg: geo.haversine_distance(geo.HUB_LAT_LONG, pkg.lat_long))
        for i in range(0, overload):
            cur_pkg = route2.manifest_optional_packages[0]
            config.packages_at_hub.append(cur_pkg)
            route1.manifest_optional_packages.remove(cur_pkg)

    route1.create_circuit()
    route2.create_circuit()

    # finally, remove packages on these routes from config.packages_at_hub
    for pkg in route1.manifest_all_packages:
        if pkg in config.packages_at_hub:
            config.packages_at_hub.remove(pkg)
    for pkg in route2.manifest_all_packages:
        if pkg in config.packages_at_hub:
            config.packages_at_hub.remove(pkg)

    return (route1, route2)