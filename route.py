import copy
from dataclasses import dataclass, field
import math

import config
import geo
import my_package
import my_time
from my_utils import get_permutations as get_permutations



class Route:

    def __init__(self, name, departure_time_as_offset):
        self.name = name
        self.truck_name = ''
        self.departure_time_as_offset = departure_time_as_offset

        self.packages_at_hub = []
        self.package_manifest = []
        self.ordered_list_of_stops = []

        self.earliest_bearing = 0.0
        self.latest_bearing = 0.0
        self.centroid = None

        # stats
        self.distance_traveled_in_miles = 0.0
        self.return_time_as_offset = -1
        self.any_package_late = False

    def __str__(self) -> str:
        slug = ""
        slug += f"{self.truck_name}: departed {my_time.convert_minutes_offset_to_time(self.departure_time_as_offset)}, returned {my_time.convert_minutes_offset_to_time(self.return_time_as_offset)}, delivered: {len(self.package_manifest)}, mileage: {self.distance_traveled_in_miles}"
        return slug

    def deep_copy(self):
        new_route = Route(self.name, self.departure_time_as_offset)
        new_route.truck_name = self.truck_name
        new_route.packages_at_hub = list(self.packages_at_hub)
        new_route.package_manifest = list(self.package_manifest)
        new_route.ordered_list_of_stops = list(self.ordered_list_of_stops)
        new_route.earliest_bearing = self.earliest_bearing
        new_route.latest_bearing = self.latest_bearing
        new_route.distance_traveled_in_miles = self.distance_traveled_in_miles
        new_route.departure_time_as_offset = self.departure_time_as_offset
        new_route.return_time_as_offset = self.return_time_as_offset
        return new_route


    def load_package_v2(self, pkg, packages_at_hub):
        if pkg not in self.package_manifest:
            self.package_manifest.append(pkg)
        if pkg in packages_at_hub:
            packages_at_hub.remove(pkg)
        self.centroid = geo.get_centroid_of_objects(self.package_manifest)
        self.recalculate_route_bearings()
        self.create_ordered_list_of_stops()
        self.update_route_stats()


    def unload_package_v2(self, pkg, packages_at_hub):
        if pkg in self.package_manifest:
            self.package_manifest.remove(pkg)
        if pkg not in packages_at_hub:
            packages_at_hub.append(pkg)
        if len(self.package_manifest) > 0:
            self.centroid = geo.get_centroid_of_objects(self.package_manifest)
            self.recalculate_route_bearings()
            self.create_ordered_list_of_stops()
        self.update_route_stats()


    def recalculate_route_bearings(self):
        list_of_angles = get_angles_between_packages_sorted_greatest_to_least(self.package_manifest)
        self.earliest_bearing = list_of_angles[0][1]
        self.latest_bearing = list_of_angles[0][0]


    def greedy_algorithm(self):
        # translate packages into stops
        stops_not_yet_added_to_path = []
        for street_address in set([x.street_address for x in self.package_manifest]):
            cur_stop = config.all_stops_by_street_address.get(street_address)
            if cur_stop not in stops_not_yet_added_to_path:
                stops_not_yet_added_to_path.append(cur_stop)

        path = [geo.HUB_STOP]
        prev_stop = geo.HUB_STOP

        # add stops to path greedily
        while stops_not_yet_added_to_path:
            stops_not_yet_added_to_path.sort(key=lambda stop: config.distances_between_pairs.get(f"{prev_stop.street_address} and {stop.street_address}"))
            cur_stop = stops_not_yet_added_to_path.pop(0)
            
            path.append(cur_stop)
            prev_stop = cur_stop
        
        path.append(geo.HUB_STOP)
        self.ordered_list_of_stops = path


    def create_ordered_list_of_stops(self):
        self.greedy_algorithm()


    def convert_ordered_list_of_stops_to_package_delivery_order(self):
        for stop in self.ordered_list_of_stops:
            for pkg in self.package_manifest:
                if pkg.street_address == stop.street_address:
                    print(f"{pkg.id} ", end='')
        print()

    
    def update_route_stats(self):

        # guard clause
        if len(self.package_manifest) == 0:
            self.any_package_late = False
            self.distance_traveled_in_miles = 0.0
            self.return_time_as_offset = self.departure_time_as_offset
            return

        # to be updated:    any_package_late: bool
        #                   distance_traveled_in_miles: float
        #                   return_time_as_offset: int
        
        self.any_package_late = False
        cur_time_as_offset = self.departure_time_as_offset
        packages_to_deliver = list(self.package_manifest)
        packages_delivered = []

        for i, stop in enumerate(self.ordered_list_of_stops):
            if i + 1 == len(self.ordered_list_of_stops):
                break
            prev_stop = stop
            cur_stop = self.ordered_list_of_stops[i+1]
            leg_distance = geo.get_distance_between_stops(prev_stop, cur_stop)
            leg_time = int(math.ceil(leg_distance * config.MINUTES_PER_MILE)) # round time up to next minute
            cur_time_as_offset += leg_time

            packages_delivered_this_stop = []
            for pkg in packages_to_deliver:
                if pkg.street_address == cur_stop.street_address:
                    packages_delivered_this_stop.append(pkg)
            for pkg in packages_delivered_this_stop:
                if pkg.deadline_as_offset < 1440: # if rush...
                        if pkg.deadline_as_offset < cur_time_as_offset: # and if late...
                            self.any_package_late = True
                            # pass
                packages_delivered.append(pkg)
                packages_to_deliver.remove(pkg)

        self.distance_traveled_in_miles = (cur_time_as_offset - self.departure_time_as_offset) * config.MILES_PER_MINUTE
        self.return_time_as_offset = cur_time_as_offset


@dataclass
class RouteList:
    routes: list[Route]
    cumulative_mileage: float = 0.0
    number_of_packages_delivered: int = 0

    def __init__(self) -> None:
        self.routes = []

    def deep_copy(self):
        new_route_list = RouteList()
        for route in self.routes:
            new_route_list.routes.append(route.deep_copy())
        new_route_list.cumulative_mileage = self.cumulative_mileage
        new_route_list.number_of_packages_delivered = self.number_of_packages_delivered
        return new_route_list

def get_angles_between_packages_sorted_greatest_to_least(list_of_packages):
    list_of_packages = list(list_of_packages)
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
    list_of_angles.sort(key=lambda x: x[0], reverse=True)
    return list_of_angles

def update_future_stops_street_addresses(departure_time_as_offset, packages_at_hub):
    packages_at_future_stops = list(filter(lambda pkg: departure_time_as_offset < pkg.when_can_leave_hub_as_offset, packages_at_hub))
    future_stops_street_addresses_set = set()
    for pkg in packages_at_future_stops:
        future_stops_street_addresses_set.add(pkg.street_address)
    return list(future_stops_street_addresses_set)


def update_rush_nonrush_packages_views(departure_time_as_offset, packages_at_hub):
    packages_at_future_stops = list(filter(lambda pkg: departure_time_as_offset < pkg.when_can_leave_hub_as_offset, packages_at_hub))
    future_stops_street_addresses_set = set()
    for pkg in packages_at_future_stops:
        future_stops_street_addresses_set.add(pkg.street_address)
    
    eligible_rush_packages = [pkg for pkg in filter(lambda pkg: pkg.deadline_as_offset < 1440 and pkg.when_can_leave_hub_as_offset <= departure_time_as_offset, packages_at_hub)]
    
    eligible_nonrush_packages = [pkg for pkg in filter(lambda pkg: pkg.deadline_as_offset == 1440 and pkg.when_can_leave_hub_as_offset <= departure_time_as_offset and pkg.street_address not in future_stops_street_addresses_set, packages_at_hub)]

    return eligible_rush_packages, eligible_nonrush_packages


def pop1_v3(departure_time_as_offset: int, packages_at_hub, truck_name):
    packages_at_hub = list(packages_at_hub) # make a copy
    orig_num_pkgs = len(packages_at_hub)

    route1 = Route('route1', departure_time_as_offset)
    route1.truck_name = truck_name

    # identify eligible packages
    eligible_rush_packages, eligible_nonrush_packages = update_rush_nonrush_packages_views(departure_time_as_offset, packages_at_hub)
    # sort packages_at_hub by soonest due, then by distance from hub
    eligible_rush_packages.sort(key=lambda pkg: pkg.when_can_leave_hub_as_offset * 100 + pkg.distance_from_hub)
    eligible_nonrush_packages.sort(key=lambda pkg: pkg.when_can_leave_hub_as_offset * 100 + pkg.distance_from_hub)

    while eligible_rush_packages and len(route1.package_manifest) < 16:
        cur_pkg = eligible_rush_packages.pop(0)
        if cur_pkg.truck_affinity and cur_pkg.truck_affinity != truck_name:
            continue
        route1.load_package_v2(cur_pkg, packages_at_hub)
        if route1.any_package_late:
            route1.unload_package_v2(cur_pkg, packages_at_hub)
            break
    
    while eligible_nonrush_packages and len(route1.package_manifest) < 16:
        cur_pkg = eligible_nonrush_packages.pop(0)
        if cur_pkg.truck_affinity and cur_pkg.truck_affinity != truck_name:
            continue
        route1.load_package_v2(cur_pkg, packages_at_hub)
        if route1.any_package_late:
            route1.unload_package_v2(cur_pkg, packages_at_hub)
            break
    
    config.came_in_left_with_1[orig_num_pkgs][len(packages_at_hub)] += 1

    return ([route1], packages_at_hub)

def pop2_v4(departure_time_as_offset: int, packages_at_hub, truck_names):
    packages_at_hub = list(packages_at_hub) # make a copy
    orig_num_pkgs = len(packages_at_hub)

    route1 = Route('route1', departure_time_as_offset)
    route1.truck_name = truck_names[0]

    route2 = Route('route2', departure_time_as_offset)
    route2.truck_name = truck_names[1]

    # if just one package, then populate one route with it and return that result
    if len(packages_at_hub) == 1:
        result = pop1_v3(departure_time_as_offset, list(packages_at_hub), 'truck 2')
        return ([result[0][0]],  list(result[1]))

    # identify eligible packages
    eligible_rush_packages, eligible_nonrush_packages = update_rush_nonrush_packages_views(departure_time_as_offset, packages_at_hub)
    # sort packages_at_hub by soonest due, then by distance from hub
    eligible_rush_packages.sort(key=lambda pkg: pkg.when_can_leave_hub_as_offset * 100 + pkg.distance_from_hub)
    eligible_nonrush_packages.sort(key=lambda pkg: pkg.when_can_leave_hub_as_offset * 100 + pkg.distance_from_hub)
    
    list_of_angles = get_angles_between_packages_sorted_greatest_to_least(eligible_rush_packages + eligible_nonrush_packages)
    sector1_bearings = (list_of_angles[0][1], list_of_angles[1][0])
    sector2_bearings = (list_of_angles[1][1], list_of_angles[0][0])

    # load route1 rush
    while eligible_rush_packages and len(route1.package_manifest) < 16:
        cur_pkg = eligible_rush_packages.pop(0)
        if cur_pkg.truck_affinity and cur_pkg.truck_affinity != route1.truck_name:
            continue
        # if geo.is_bearing_in_angle(cur_pkg.bearing_from_hub, sector1_bearings[0], sector1_bearings[1]):
        route1.load_package_v2(cur_pkg, packages_at_hub)
        if route1.any_package_late:
            route1.unload_package_v2(cur_pkg, packages_at_hub)
            break

    # load route1 nonrush
    while eligible_nonrush_packages and len(route1.package_manifest) < 16:
        cur_pkg = eligible_nonrush_packages.pop(0)
        if cur_pkg.truck_affinity and cur_pkg.truck_affinity != route1.truck_name:
            continue
        # if geo.is_bearing_in_angle(cur_pkg.bearing_from_hub, sector1_bearings[0], sector1_bearings[1]):
        route1.load_package_v2(cur_pkg, packages_at_hub)
        if route1.any_package_late:
            route1.unload_package_v2(cur_pkg, packages_at_hub)
            break

    # recalculate eligible packages
    eligible_rush_packages, eligible_nonrush_packages = update_rush_nonrush_packages_views(departure_time_as_offset, packages_at_hub)
    # sort packages_at_hub by soonest due, then by distance from hub
    eligible_rush_packages.sort(key=lambda pkg: pkg.when_can_leave_hub_as_offset * 100 + pkg.distance_from_hub)
    eligible_nonrush_packages.sort(key=lambda pkg: pkg.when_can_leave_hub_as_offset * 100 + pkg.distance_from_hub)

     # load route2 rush
    while eligible_rush_packages and len(route2.package_manifest) < 16:
        cur_pkg = eligible_rush_packages.pop(0)
        if cur_pkg.truck_affinity and cur_pkg.truck_affinity != route2.truck_name:
            continue
        # if geo.is_bearing_in_angle(cur_pkg.bearing_from_hub, sector1_bearings[0], sector1_bearings[1]):
        route2.load_package_v2(cur_pkg, packages_at_hub)
        if route2.any_package_late:
            route2.unload_package_v2(cur_pkg, packages_at_hub)
            break

    # load route2 nonrush
    while eligible_nonrush_packages and len(route2.package_manifest) < 16:
        cur_pkg = eligible_nonrush_packages.pop(0)
        if cur_pkg.truck_affinity and cur_pkg.truck_affinity != route2.truck_name:
            continue
        # if geo.is_bearing_in_angle(cur_pkg.bearing_from_hub, sector1_bearings[0], sector1_bearings[1]):
        route2.load_package_v2(cur_pkg, packages_at_hub)
        if route2.any_package_late:
            route2.unload_package_v2(cur_pkg, packages_at_hub)
            break


    config.came_in_left_with_2[orig_num_pkgs][len(packages_at_hub)] += 1

    return ([route1, route2], packages_at_hub)


