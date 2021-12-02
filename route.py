import copy
from dataclasses import dataclass
import math

import config
import geo
import my_package
import my_time




class Route:

    def __init__(self, name):
        self.name = name
        self.truck_number = 0

        self.packages_at_hub = []
        self.package_manifest = []
        self.manifest_all_packages = []
        self.manifest_required_packages = []
        self.manifest_optional_packages = []

        self.stops_not_yet_added_to_path = []

        self.circuit = []
        # path_to_farthest = []
        # path_from_farthest = []

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
            if len(self.manifest_all_packages) == 16:
                break
            if pkg not in self.manifest_all_packages:
                if pkg.street_address in existing_addresses:
                    self.add_optional_package(pkg)
                    self.combine_manifests_required_optional_packages()

    def update_route_bearings_per_new_package(self, pkg):
        if not geo.is_bearing_in_angle(pkg.bearing_from_hub, self.earliest_bearing, self.latest_bearing):
            if geo.get_angle(self.latest_bearing, pkg.bearing_from_hub) < geo.get_angle(pkg.bearing_from_hub, self.earliest_bearing):
                self.latest_bearing = pkg.bearing_from_hub
            else:
                self.earliest_bearing = pkg.bearing_from_hub

    def update_route_bearings_per_removed_package(self, pkg):
        self.recalculate_route_bearings()

    def recalculate_route_bearings(self):
        list_of_angles = get_angles_between_packages_sorted_greatest_to_least(self.manifest_all_packages)
        self.earliest_bearing = list_of_angles[0][1]
        self.latest_bearing = list_of_angles[0][0]

    def remove_package_from_manifest(self, pkg, packages_at_hub):
        if pkg in self.manifest_required_packages:
            self.manifest_required_packages.remove(pkg)
        if pkg in self.manifest_optional_packages:
            self.manifest_optional_packages.remove(pkg)
        self.combine_manifests_required_optional_packages()
        if pkg not in packages_at_hub:
            packages_at_hub.add(pkg)
        self.update_route_bearings_per_removed_package(pkg)

    def add_required_package(self, pkg):
        self.add_package_to_a_manifest(pkg, self.manifest_required_packages)

    def add_optional_package(self, pkg):
        # print(f"trying to add pkg id {pkg.id} as optional")
        self.add_package_to_a_manifest(pkg, self.manifest_optional_packages)
    
    def add_package_to_a_manifest(self, pkg, a_manifest):
        if pkg not in a_manifest:
            a_manifest.append(pkg)
            if pkg in self.packages_at_hub:
                self.packages_at_hub.remove(pkg)
            self.combine_manifests_required_optional_packages()
            self.update_route_bearings_per_new_package(pkg)

    def load_package(self, pkg, source, target_manifest):
        if pkg not in target_manifest:
            target_manifest.append(pkg)
        if pkg in source:
            source.remove(pkg)
        if pkg in self.packages_at_hub:
            self.packages_at_hub.remove(pkg)
        self.combine_manifests_required_optional_packages()
        self.recalculate_route_bearings()

    def unload_package(self, pkg, source_manifest, target):
        if pkg in source_manifest:
            source_manifest.remove(pkg)
        if pkg not in target:
            target.append(pkg)
        if pkg not in self.packages_at_hub:
            self.packages_at_hub.add(pkg)
        self.combine_manifests_required_optional_packages()
        self.recalculate_route_bearings()




    def combine_manifests_required_optional_packages(self):
        self.manifest_all_packages = self.manifest_required_packages + self.manifest_optional_packages


    def create_circuit(self):
        # translate packages into stops
        for street_address in set([x.street_address for x in self.manifest_all_packages]):
            cur_stop = config.all_stops_by_street_address.get(street_address)
            if cur_stop not in self.stops_not_yet_added_to_path:
                self.stops_not_yet_added_to_path.append(cur_stop)

        # sort stops in descending distance from weighted center
        self.weighted_center = geo.get_weighted_center_of_objects(self.stops_not_yet_added_to_path)
        self.stops_not_yet_added_to_path.sort(key=lambda stop: geo.haversine_distance(geo.HUB_LAT_LONG, stop.lat_long), reverse=True)
        self.farthest_stop = self.stops_not_yet_added_to_path[0]

        path_to_farthest = [geo.HUB_STOP] + [self.farthest_stop]
        path_from_farthest = [self.farthest_stop] + [geo.HUB_STOP]
        self.stops_not_yet_added_to_path.remove(self.farthest_stop)
        for cur_stop in list(self.stops_not_yet_added_to_path):
            if geo.is_bearing_in_angle(cur_stop.bearing_from_hub, self.earliest_bearing, self.farthest_stop.bearing_from_hub):
                cur_least_distance = float('inf')
                index_insert_after = -1
                for i in range(0, len(path_to_farthest) - 1):
                    cur_distance = geo.distance_of_path_of_stops([path_to_farthest[i]] + [cur_stop] + [path_to_farthest[i+1]])
                    if cur_distance < cur_least_distance:
                        cur_least_distance = cur_distance
                        index_insert_after = i
                path_to_farthest.insert(i + 1, cur_stop)
            else:
                cur_least_distance = float('inf')
                index_insert_after = -1
                for i in range(0, len(path_from_farthest) - 1):
                    cur_distance = geo.distance_of_path_of_stops([path_from_farthest[i]] + [cur_stop] + [path_from_farthest[i+1]])
                    if cur_distance < cur_least_distance:
                        cur_least_distance = cur_distance
                        index_insert_after = i
                path_from_farthest.insert(i + 1, cur_stop)
            self.stops_not_yet_added_to_path.remove(cur_stop)

        self.circuit = path_to_farthest + path_from_farthest[1:]

    def convert_circuit_to_package_delivery_order(self):
        for stop in self.circuit:
            for pkg in self.manifest_all_packages:
                if pkg.street_address == stop.street_address:
                    print(f"{pkg.id} ", end='')
        print()

@dataclass
class SimpleRoute:
    truck_name: str
    departure_time: str
    ordered_list_of_stops: list[geo.Stop]
    list_of_packages: list[my_package.Package]
    # fields computed by validation function
    return_time: str
    distance_traveled_in_miles: int = 0
    miles_per_package: float = 0
    
    

def validate_simple_route(simple_route):
    if validate_simple_route_helper(simple_route):
        return True
    reversed_route = copy.deepcopy(simple_route)
    if validate_simple_route_helper(reversed_route):
        simple_route = reversed_route
        return True
    return False
        

def validate_simple_route_helper(simple_route):
    departure_time_as_offset = my_time.convert_time_to_minutes_offset(simple_route.departure_time)
    cur_time_as_offset = departure_time_as_offset
    packages_to_deliver = list(simple_route.list_of_packages)
    packages_delivered = []
    at_least_one_package_delivered_late = False

    # print(f"leaving hub at {my_time.convert_minutes_offset_to_time(cur_time_as_offset)}")

    for i, stop in enumerate(simple_route.ordered_list_of_stops):
        if i + 1 == len(simple_route.ordered_list_of_stops):
            break
        prev_stop = stop
        cur_stop = simple_route.ordered_list_of_stops[i+1]
        leg_distance = geo.get_distance_between_stops(prev_stop, cur_stop)
        leg_time = leg_distance * config.MINUTES_PER_MILE
        cur_time_as_offset = int(math.ceil(cur_time_as_offset + leg_time)) # round time up to next minute

        # print(f"arriving at {cur_stop.street_address} at {my_time.convert_minutes_offset_to_time(cur_time_as_offset)}")

        packages_delivered_this_stop = []
        for pkg in packages_to_deliver:
            if pkg.street_address == cur_stop.street_address:
                packages_delivered_this_stop.append(pkg)
                packages_delivered.append(pkg)
                if pkg.deadline_as_offset < 1440:
                    if pkg.deadline_as_offset < cur_time_as_offset:
                        at_least_one_package_delivered_late = True
                #         print(f"    rush pkg with id {pkg.id} delivered LATE at {my_time.convert_minutes_offset_to_time(cur_time_as_offset)} (due at {my_time.convert_minutes_offset_to_time(pkg.deadline_as_offset)})")
                #     else:
                #         print(f"    rush pkg with id {pkg.id} delivered in time at {my_time.convert_minutes_offset_to_time(cur_time_as_offset)} (due at {my_time.convert_minutes_offset_to_time(pkg.deadline_as_offset)})")
                # else:
                #     print(f"         pkg with id {pkg.id} delivered at {my_time.convert_minutes_offset_to_time(cur_time_as_offset)}")
        for pkg in packages_delivered_this_stop:
            packages_to_deliver.remove(pkg)
    
    simple_route.return_time = my_time.convert_minutes_offset_to_time(cur_time_as_offset)
    simple_route.distance_traveled_in_miles = (cur_time_as_offset - departure_time_as_offset) * config.MILES_PER_MINUTE
    simple_route.miles_per_package = simple_route.distance_traveled_in_miles / len(packages_delivered)
    
    # print(f"back to hub at {my_time.convert_minutes_offset_to_time(cur_time_as_offset)}")
    # print(sorted([x.id for x in packages_delivered]))
    
    return not at_least_one_package_delivered_late
    


def validate_route(a_route, departure_time, reverse):
    departure_time_as_offset = my_time.convert_time_to_minutes_offset(departure_time)
    cur_time_as_offset = departure_time_as_offset
    packages_to_deliver = list(a_route.manifest_all_packages)
    packages_delivered = []
    at_least_one_package_delivered_late = False

    the_circuit = a_route.circuit
    if reverse == True:
        the_circuit.reverse()

    # print(f"leaving hub at {my_time.convert_minutes_offset_to_time(cur_time_as_offset)}")

    for i, stop in enumerate(the_circuit):
        if i + 1 == len(the_circuit):
            break
        prev_stop = stop
        cur_stop = the_circuit[i+1]
        leg_distance = geo.get_distance_between_stops(prev_stop, cur_stop)
        leg_time = leg_distance * config.MINUTES_PER_MILE
        cur_time_as_offset = int(math.ceil(cur_time_as_offset + leg_time)) # round time up to next minute

        # print(f"arriving at {cur_stop.street_address} at {my_time.convert_minutes_offset_to_time(cur_time_as_offset)}")

        packages_delivered_this_stop = []
        for pkg in packages_to_deliver:
            if pkg.street_address == cur_stop.street_address:
                packages_delivered_this_stop.append(pkg)
                packages_delivered.append(pkg)
                if pkg.deadline_as_offset < 1440:
                    if pkg.deadline_as_offset < cur_time_as_offset:
                        at_least_one_package_delivered_late = True
                #         print(f"    rush pkg with id {pkg.id} delivered LATE at {my_time.convert_minutes_offset_to_time(cur_time_as_offset)} (due at {my_time.convert_minutes_offset_to_time(pkg.deadline_as_offset)})")
                #     else:
                #         print(f"    rush pkg with id {pkg.id} delivered in time at {my_time.convert_minutes_offset_to_time(cur_time_as_offset)} (due at {my_time.convert_minutes_offset_to_time(pkg.deadline_as_offset)})")
                # else:
                #     print(f"         pkg with id {pkg.id} delivered at {my_time.convert_minutes_offset_to_time(cur_time_as_offset)}")
        for pkg in packages_delivered_this_stop:
            packages_to_deliver.remove(pkg)
    
    total_mileage = (cur_time_as_offset - departure_time_as_offset) * config.MILES_PER_MINUTE
    miles_per_package = total_mileage / len(packages_delivered)
    # print(f"back to hub at {my_time.convert_minutes_offset_to_time(cur_time_as_offset)}")
    print(sorted([x.id for x in packages_delivered]))
    config.cumulative_miles += total_mileage
    return (not at_least_one_package_delivered_late, total_mileage, len(packages_delivered), miles_per_package, departure_time, my_time.convert_minutes_offset_to_time(cur_time_as_offset))


def populate_one_route(departure_time: str, packages_at_hub):
    packages_at_hub = list(packages_at_hub) # make a copy

    # print([pkg.id for pkg in packages_at_hub])

    rush_packages_ready = [x for x in filter(lambda x: x.deadline_as_offset < 1440 and x.when_can_leave_hub <= my_time.convert_time_to_minutes_offset(departure_time), packages_at_hub)]
    
    nonrush_packages_ready = [x for x in filter(lambda x: x.deadline_as_offset == 1440 and x.when_can_leave_hub <= my_time.convert_time_to_minutes_offset(departure_time), packages_at_hub)]

    # 3.1 create package affinity group, if necessary
    p_ids_in_affinity = set()
    treat_affinity_packages_as_rush = False
    for pkg in rush_packages_ready:
        if pkg.package_affinities != {0}:
            p_ids_in_affinity.add(pkg.id)
            p_ids_in_affinity.update(pkg.package_affinities)
            treat_affinity_packages_as_rush = True
    for pkg in nonrush_packages_ready:
        if pkg.package_affinities != {0}:
            p_ids_in_affinity.add(pkg.id)
            p_ids_in_affinity.update(pkg.package_affinities)
    affinity_packages_ready = []
    for p_id in p_ids_in_affinity:
        cur_pkg = config.all_packages_by_id[p_id]
        affinity_packages_ready.append(cur_pkg)
        if cur_pkg in packages_at_hub:
            packages_at_hub.remove(cur_pkg)
        if cur_pkg in rush_packages_ready:
            rush_packages_ready.remove(cur_pkg)
        if cur_pkg in nonrush_packages_ready:
            nonrush_packages_ready.remove(cur_pkg)
    
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

    # 5. add seed packages to route
    route1 = Route('route1')
    route1.packages_at_hub = packages_at_hub
    # list_of_angles = get_angles_between_packages_sorted_greatest_to_least(seed_packages)
    # route1.earliest_bearing = list_of_angles[0][1]
    # route1.latest_bearing = list_of_angles[0][0]
    for pkg in rush_packages_ready:
        route1.add_required_package(pkg)
    
    if affinity_packages_ready:
        if treat_affinity_packages_as_rush:
            for pkg in affinity_packages_ready:
                route1.add_required_package(pkg)
        else:
            if route1.manifest_all_packages + len(affinity_packages_ready) <= 16:
                for pkg in affinity_packages_ready:
                    route1.add_optional_package(pkg)

    # 6. add optional packages at existing stops
    # TODO: change this to add them in decreasing order of distance from hub
    if rush_packages_ready:
        route1.add_optional_packages_at_existing_stops(nonrush_packages_ready)

    # 8. check whether we have enough or too many packages and if we're on time
    # only packages added thus far should be: rush + colocated nonrush + package affinity

    if len(route1.manifest_all_packages) == 0: # route has no packages as of yet
        # add package farthest away from hub, then add packages in decreasing order of distance from the dynamically updated weighted center of the manifest
        nonrush_packages_ready.sort(key=lambda pkg: geo.haversine_distance(geo.HUB_LAT_LONG, pkg.lat_long), reverse=True)
        farthest_pkg = nonrush_packages_ready[0]
        route1.load_package(farthest_pkg, nonrush_packages_ready, route1.manifest_optional_packages)
        # sort by increasing combined distance from farthest_pkg and hub
        nonrush_packages_ready.sort(key=lambda pkg: geo.haversine_distance(geo.HUB_LAT_LONG, pkg.lat_long) + geo.haversine_distance(farthest_pkg.lat_long, pkg.lat_long))
        for i in range(0, min(15, len(nonrush_packages_ready))): # 15, since 15 packages + the `farthest_pkg` added a few lines earlier == 16 packages limit
            cur_package = nonrush_packages_ready[i]
            route1.add_optional_package(cur_package)
            # TODO: check whether this breaks the route in both directions
            # if it doesn't, then proceed
            # if it does, then undo the last package added and break the for loop
    elif 0 < len(route1.manifest_all_packages) < 16: # route is underloaded, so add more optional packages
        weighted_center = geo.get_weighted_center_of_objects(route1.manifest_all_packages)

        # sort by increasing combined distance from weighted_center and hub
        nonrush_packages_ready.sort(key=lambda pkg: geo.haversine_distance(weighted_center, pkg.lat_long) + geo.haversine_distance(geo.HUB_LAT_LONG, pkg.lat_long))
        num_packages_needed = 16 - len(route1.manifest_all_packages)
        for i in range(0, min(num_packages_needed, len(nonrush_packages_ready))):
            cur_package = nonrush_packages_ready[i]
            route1.add_optional_package(cur_package)
    elif len(route1.manifest_all_packages) == 16: # route is already fully loaded, so do nothing
        pass
    else: # len(route1.manifest_all_packages) > 16 # # # route is overloaded, so remove some optional packages
        overload = len(route1.manifest_all_packages) - 16
        # find the n optional packages closest to the hub and remove them from the manifest
        route1.manifest_optional_packages.sort(key=lambda pkg: geo.haversine_distance(geo.HUB_LAT_LONG, pkg.lat_long))
        for i in range(0, min(overload, len(route1.manifest_optional_packages))):
            cur_pkg = route1.manifest_optional_packages[0]
            route1.remove_package_from_manifest(cur_pkg, packages_at_hub)
        
            


    # TODO: create quick validate_path() function that takes a path of packages, whether reverse=False or reverse=True, and returns whether any packages are late; we can keep adding packages until something is late, then fall back on last good path

    # but if we don't have any packages so far, then find the sector that includes all optional packages and proceed
    # if len(route1.manifest_all_packages) < 16:
    #     num_packages_needed = 16 - len(route1.manifest_all_packages)
    #     s = slice(0, min(num_packages_needed, len(nonrush_packages_ready)))
    #     packages_to_add = list(nonrush_packages_ready[s])
    #     for pkg in packages_to_add:
    #         route1.add_optional_package(pkg)

    route1.create_circuit()

    # finally, remove packages on these routes from packages_at_hub
    for pkg in route1.manifest_all_packages:
        if pkg in packages_at_hub:
            packages_at_hub.remove(pkg)

    return (route1, packages_at_hub)


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


def populate_two_routes(departure_time: str, packages_at_hub):
    
    rush_packages_ready = [x for x in filter(lambda x: x.deadline_as_offset < 1440 and x.when_can_leave_hub == my_time.convert_time_to_minutes_offset(departure_time), packages_at_hub)]
    
    nonrush_packages_ready = [x for x in filter(lambda x: x.deadline_as_offset == 1440 and x.when_can_leave_hub == my_time.convert_time_to_minutes_offset(departure_time), packages_at_hub)]

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
        if cur_pkg in packages_at_hub:
            packages_at_hub.remove(cur_pkg)
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
            packages_at_hub.append(cur_pkg)
            route1.manifest_optional_packages.remove(cur_pkg)
    if len(route2.manifest_all_packages) > 16:
        overload = len(route2.manifest_all_packages) - 16
        # find the n packages closest to the hub and remove them from the manifest
        route2.manifest_optional_packages.sort(key=lambda pkg: geo.haversine_distance(geo.HUB_LAT_LONG, pkg.lat_long))
        for i in range(0, overload):
            cur_pkg = route2.manifest_optional_packages[0]
            packages_at_hub.append(cur_pkg)
            route1.manifest_optional_packages.remove(cur_pkg)

    route1.create_circuit()
    route2.create_circuit()

    # finally, remove packages on these routes from config.packages_at_hub
    for pkg in route1.manifest_all_packages:
        if pkg in config.packages_at_hub:
            packages_at_hub.remove(pkg)
    for pkg in route2.manifest_all_packages:
        if pkg in config.packages_at_hub:
            packages_at_hub.remove(pkg)

    return (route1, route2, packages_at_hub)