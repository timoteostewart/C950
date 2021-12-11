import copy
from dataclasses import dataclass, field
import math

import config
import geo
import my_package
import my_time
import truck



class Route:

    def __init__(self, name, departure_time_as_offset):
        self.name = name
        self.truck_name = ''
        self.departure_time_as_offset = departure_time_as_offset

        self.packages_at_hub = []
        
        self.package_manifest = []
        self.list_of_required_packages = []
        self.list_of_optional_packages = []

        self.ordered_list_of_stops = []

        self.earliest_bearing = 0.0
        self.latest_bearing = 0.0

        self.centroid = None

        # stats
        self.distance_traveled_in_miles = 0.0
        self.return_time_as_offset = -1
        self.miles_per_package = 0.0
        any_package_late = False

    def __str__(self) -> str:
        slug = ""
        slug += f"{self.truck_name}: departed {my_time.convert_minutes_offset_to_time(self.departure_time_as_offset)}, returned {my_time.convert_minutes_offset_to_time(self.return_time_as_offset)}, delivered: {len(self.package_manifest)}, mileage: {self.distance_traveled_in_miles}"
        return slug

    def deep_copy(self):
        new_route = Route(self.name, self.departure_time_as_offset)
        new_route.truck_name = self.truck_name
        new_route.packages_at_hub = list(self.packages_at_hub)
        new_route.package_manifest = list(self.package_manifest)
        new_route.list_of_required_packages = list(self.list_of_required_packages)
        new_route.list_of_optional_packages = list(self.list_of_optional_packages)
        new_route.ordered_list_of_stops = list(self.ordered_list_of_stops)
        new_route.earliest_bearing = self.earliest_bearing
        new_route.latest_bearing = self.latest_bearing
        new_route.distance_traveled_in_miles = self.distance_traveled_in_miles
        new_route.departure_time_as_offset = self.departure_time_as_offset
        new_route.return_time_as_offset = self.return_time_as_offset
        return new_route

    def massage_stops_into_better_order_if_possible(self):
        # TODO
        pass

    def add_optional_packages_at_existing_stops(self, nonrush_packages_ready):
        # TODO: don't add for future stops
        existing_addresses = {x.street_address for x in self.list_of_required_packages}
        for pkg in nonrush_packages_ready:
            if len(self.package_manifest) == 16:
                break
            if pkg not in self.package_manifest:
                if pkg.street_address in existing_addresses:
                    self.load_package_as_optional(pkg)
                    self.combine_lists_of_required_and_optional_packages()


    def load_package2(self, pkg, packages_at_hub):
        if pkg not in self.package_manifest:
            self.package_manifest.append(pkg)
        if pkg in packages_at_hub:
            packages_at_hub.remove(pkg)
        self.centroid = geo.get_centroid_of_objects(self.package_manifest)
        self.recalculate_route_bearings()
        self.create_ordered_list_of_stops()
        self.update_route_stats()

    def unload_package2(self, pkg, packages_at_hub):
        if pkg in self.package_manifest:
            self.package_manifest.remove(pkg)
        if pkg not in packages_at_hub:
            packages_at_hub.append(pkg)
        if len(self.package_manifest) > 0:
            self.centroid = geo.get_centroid_of_objects(self.package_manifest)
            self.recalculate_route_bearings()
            self.create_ordered_list_of_stops()
        self.update_route_stats()


    def new_load_package_as_required(self, pkg, packages_at_hub):
        self.load_package(pkg, self.packages_at_hub, self.list_of_required_packages)
        packages_at_hub.remove(pkg)

    def new_unload_package_as_required(self, pkg, packages_at_hub):
        self.load_package(pkg, self.packages_at_hub, self.list_of_optional_packages)
        packages_at_hub.append(pkg)

    def new_load_optional_package(self, pkg, packages_at_hub):
        self.load_package(pkg, self.packages_at_hub, self.list_of_optional_packages)
        packages_at_hub.remove(pkg)

    def new_unload_optional_package(self, pkg, packages_at_hub):
        self.unload_package(pkg, self.list_of_optional_packages, self.packages_at_hub)
        packages_at_hub.append(pkg)



    def load_package_as_required(self, pkg):
        self.load_package(pkg, self.packages_at_hub, self.list_of_required_packages)

    def load_package_as_optional(self, pkg):
        self.load_package(pkg, self.packages_at_hub, self.list_of_optional_packages)
    
    def unload_required_package(self, pkg):
        self.unload_package(pkg, self.list_of_required_packages, self.packages_at_hub)

    def unload_optional_package(self, pkg):
        self.unload_package(pkg, self.list_of_optional_packages, self.packages_at_hub)

    def load_package(self, pkg, source, target_list_of_packages):
        if pkg not in target_list_of_packages:
            target_list_of_packages.append(pkg)
        if pkg in source:
            source.remove(pkg)
        if pkg in self.packages_at_hub:
            self.packages_at_hub.remove(pkg)
        self.combine_lists_of_required_and_optional_packages()
        self.centroid = geo.get_centroid_of_objects(self.package_manifest)
        self.recalculate_route_bearings()
        self.create_ordered_list_of_stops()
        self.update_route_stats

    def unload_package(self, pkg, source_list_of_packages, target):
        if pkg in source_list_of_packages:
            source_list_of_packages.remove(pkg)
        if pkg not in target:
            target.append(pkg)
        if pkg not in self.packages_at_hub:
            self.packages_at_hub.append(pkg)
        self.combine_lists_of_required_and_optional_packages()

        if len(self.package_manifest) > 0:
            self.centroid = geo.get_centroid_of_objects(self.package_manifest)
            self.recalculate_route_bearings()
            self.create_ordered_list_of_stops()
            self.update_route_stats

    def combine_lists_of_required_and_optional_packages(self):
        self.package_manifest = self.list_of_required_packages + self.list_of_optional_packages

    def recalculate_route_bearings(self):
        list_of_angles = get_angles_between_packages_sorted_greatest_to_least(self.package_manifest)
        self.earliest_bearing = list_of_angles[0][1]
        self.latest_bearing = list_of_angles[0][0]

    def create_ordered_list_of_stops(self):
        # translate packages into stops
        stops_not_yet_added_to_path = []
        for street_address in set([x.street_address for x in self.package_manifest]):
            cur_stop = config.all_stops_by_street_address.get(street_address)
            if cur_stop not in stops_not_yet_added_to_path:
                stops_not_yet_added_to_path.append(cur_stop)

        # sort stops in decreasing distance from hub
        stops_not_yet_added_to_path.sort(key=lambda stop: geo.haversine_distance(geo.HUB_LAT_LONG, stop.lat_long), reverse=True)
        
        farthest_stop = stops_not_yet_added_to_path[0]
        path_to_farthest = [geo.HUB_STOP] + [farthest_stop]
        path_from_farthest = [farthest_stop] + [geo.HUB_STOP]
        stops_not_yet_added_to_path.remove(farthest_stop)
        
        for cur_stop in list(stops_not_yet_added_to_path):
            if geo.is_bearing_in_angle(cur_stop.bearing_from_hub, self.earliest_bearing, farthest_stop.bearing_from_hub):
                cur_least_distance = float('inf')
                index_insert_after = -1
                for i in range(0, len(path_to_farthest) - 1):
                    cur_distance = geo.distance_of_path_of_stops([path_to_farthest[i]] + [cur_stop] + [path_to_farthest[i+1]])
                    if cur_distance < cur_least_distance:
                        cur_least_distance = cur_distance
                        index_insert_after = i
                path_to_farthest.insert(index_insert_after + 1, cur_stop)
            else:
                cur_least_distance = float('inf')
                index_insert_after = -1
                for i in range(0, len(path_from_farthest) - 1):
                    cur_distance = geo.distance_of_path_of_stops([path_from_farthest[i]] + [cur_stop] + [path_from_farthest[i+1]])
                    if cur_distance < cur_least_distance:
                        cur_least_distance = cur_distance
                        index_insert_after = i
                path_from_farthest.insert(index_insert_after + 1, cur_stop)
            stops_not_yet_added_to_path.remove(cur_stop)
        self.ordered_list_of_stops = path_to_farthest + path_from_farthest[1:]


    def convert_ordered_list_of_stops_to_package_delivery_order(self):
        for stop in self.ordered_list_of_stops:
            for pkg in self.package_manifest:
                if pkg.street_address == stop.street_address:
                    print(f"{pkg.id} ", end='')
        print()

    
    def update_route_stats(self):
        # updates:  distance_traveled_in_miles: float
        #           miles_per_package
        #           return_time_as_offset: int
        #           any_package_late: bool
        
        self.any_package_late = False

        if len(self.ordered_list_of_stops) < 3:
            self.distance_traveled_in_miles = float('inf')
            return
        
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
                    if pkg.deadline_as_offset < 1440:
                        if pkg.deadline_as_offset < cur_time_as_offset:
                            self.any_package_late = True
            for pkg in packages_delivered_this_stop:
                packages_delivered.append(pkg)
                packages_to_deliver.remove(pkg)
        
        if packages_to_deliver:
            self.distance_traveled_in_miles = float('inf') # failed to deliver all packages

        self.distance_traveled_in_miles = (cur_time_as_offset - self.departure_time_as_offset) * config.MILES_PER_MINUTE
        self.miles_per_package = self.distance_traveled_in_miles / len(packages_delivered)
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


def validate_route(route):
    if len(route.ordered_list_of_stops) == 0:
        return False
    if validate_route_helper(route):
        return True
    route.ordered_list_of_stops.reverse()
    return validate_route_helper(route)

def validate_route_helper(route):
    cur_time_as_offset = route.departure_time_as_offset
    packages_to_deliver = list(route.package_manifest)
    packages_delivered = []

    for i, stop in enumerate(route.ordered_list_of_stops):
        if i + 1 == len(route.ordered_list_of_stops):
            break
        prev_stop = stop
        cur_stop = route.ordered_list_of_stops[i+1]
        leg_distance = geo.get_distance_between_stops(prev_stop, cur_stop)
        leg_time = leg_distance * config.MINUTES_PER_MILE
        cur_time_as_offset = int(math.ceil(cur_time_as_offset + leg_time)) # round time up to next minute

        packages_delivered_this_stop = []
        for pkg in packages_to_deliver:
            if pkg.street_address == cur_stop.street_address:
                packages_delivered_this_stop.append(pkg)
                packages_delivered.append(pkg)
                if pkg.deadline_as_offset < 1440:
                    if pkg.deadline_as_offset < cur_time_as_offset:
                        return False # late packages are unacceptable
        for pkg in packages_delivered_this_stop:
            packages_to_deliver.remove(pkg)
    
    # if packages_to_deliver:
    #     return False # failed to deliver all packages

    route.distance_traveled_in_miles = (cur_time_as_offset - route.departure_time_as_offset) * config.MILES_PER_MINUTE
    route.miles_per_package = route.distance_traveled_in_miles / len(packages_delivered)
    
    return True # if we reached here, we delivered all packages and there were no late packages


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


def new_pop1(departure_time_as_offset: int, packages_at_hub, truck_name):
    packages_at_hub = list(packages_at_hub) # make a copy

    route1 = Route('route1', departure_time_as_offset)
    route1.truck_name = truck_name

    rush_packages_ready_view, nonrush_packages_ready_view = update_rush_nonrush_packages_views(departure_time_as_offset, packages_at_hub)
    
    future_stops_street_addresses = update_future_stops_street_addresses(departure_time_as_offset, packages_at_hub)
    nonrush_packages_not_at_future_stops = list(filter(lambda pkg: pkg.street_address not in future_stops_street_addresses, nonrush_packages_ready_view))

    # I. if there are rush affinity packages, seed route1 with those packages
    p_ids_in_affinity = set()
    affinity_packages_are_rush = False
    for pkg in rush_packages_ready_view:
        if pkg.package_affinities != {0}:
            p_ids_in_affinity.add(pkg.id)
            p_ids_in_affinity.update(pkg.package_affinities)
            affinity_packages_are_rush = True
    for pkg in nonrush_packages_ready_view:
        if pkg.package_affinities != {0}:
            p_ids_in_affinity.add(pkg.id)
            p_ids_in_affinity.update(pkg.package_affinities)
    affinity_packages_ready = []
    for p_id in p_ids_in_affinity:
        cur_pkg = config.all_packages_by_id[p_id]
        affinity_packages_ready.append(cur_pkg)
        if cur_pkg in packages_at_hub:
            packages_at_hub.remove(cur_pkg)
    if affinity_packages_ready and affinity_packages_are_rush:
        for pkg in affinity_packages_ready:
            route1.load_package2(pkg, packages_at_hub)

    rush_packages_ready_view, nonrush_packages_ready_view = update_rush_nonrush_packages_views(departure_time_as_offset, packages_at_hub)

    # II. if there are no rush affinity packages but there are rush packages, seed route1 with the fartehest-away one
    if rush_packages_ready_view and not (affinity_packages_ready and affinity_packages_are_rush):
        rush_packages_ready_view.sort(key=lambda pkg: pkg.distance_from_hub, reverse=True)
        farthest_away_rush_package = rush_packages_ready_view[0]
        route1.load_package2(farthest_away_rush_package, packages_at_hub)

    # III. if there are no rush packages, seed route1 with farthest away nonrush package not at future stops
    nonrush_packages_not_at_future_stops = list(filter(lambda pkg: pkg.street_address not in future_stops_street_addresses, nonrush_packages_ready_view))
    if not rush_packages_ready_view and not (affinity_packages_ready and affinity_packages_are_rush):
        if nonrush_packages_not_at_future_stops:
            nonrush_packages_not_at_future_stops.sort(key=lambda pkg: pkg.distance_from_hub, reverse=True)
            route1.load_package2(nonrush_packages_not_at_future_stops[0], packages_at_hub)

    # IV. if we still haven't been able to seed route1 by this point, then return a dummy route that will be discarded
    if not route1.package_manifest:
        route1.distance_traveled_in_miles = float('inf')
        return (route1, [])

    

    #
    # continue populating route1
    #

    # TODO: implement truck affinity group logic

    # # # 3.2 create truck affinity group
    # affinity_truck_ready = []
    # for pkg in rush_packages_ready:
    #     if pkg.truck_affinity != 0:
    #         affinity_truck_ready.add(pkg)
    #         rush_packages_ready.remove(pkg)
    #         packages_at_hub.remove(pkg)
    # for pkg in nonrush_packages_ready:
    #     if pkg.truck_affinity != 0:
    #         affinity_truck_ready.append(pkg)
    #         nonrush_packages_ready.remove(pkg)
    #         packages_at_hub.remove(pkg)
    # exists_truck_affinity_group = affinity_truck_ready
    # if exists_truck_affinity_group and truck_name == 'truck 2':
    #     for pkg in affinity_truck_ready:
    #         nonrush_packages_ready.append(pkg)


    # 5. add rush packages to route
    rush_packages_ready_view, nonrush_packages_ready_view = update_rush_nonrush_packages_views(departure_time_as_offset, packages_at_hub)
    nonrush_packages_not_at_future_stops = list(filter(lambda pkg: pkg.street_address not in future_stops_street_addresses, nonrush_packages_ready_view))

    # 5a. add nonrush packages not at future stops to route

    # nonrush_packages_not_at_future_stops = list(filter(lambda pkg: pkg.street_address not in future_stops_street_addresses, nonrush_packages_ready_view))

    if rush_packages_ready_view:
        rush_packages_ready_view.sort(key=lambda pkg: geo.haversine_distance(pkg.lat_long, route1.centroid))
        for pkg in rush_packages_ready_view:
            if len(route1.package_manifest) == 16:
                break
            route1.load_package2(pkg, packages_at_hub)
            if route1.any_package_late:
                route1.unload_package2(pkg, packages_at_hub)


    # 6. add optional packages at existing non future stops
    # TODO: change this to add them in decreasing order of distance from hub

    # 7. add more packages not at future stops



    return (route1, packages_at_hub)

def update_rush_nonrush_packages_views(departure_time_as_offset, packages_at_hub):
    rush_packages_ready_view = [x for x in filter(lambda x: x.deadline_as_offset < 1440 and x.when_can_leave_hub_as_offset <= departure_time_as_offset, packages_at_hub)]
    nonrush_packages_ready_view = [x for x in filter(lambda x: x.deadline_as_offset == 1440 and x.when_can_leave_hub_as_offset <= departure_time_as_offset, packages_at_hub)]
    return rush_packages_ready_view, nonrush_packages_ready_view

def update_future_stops_street_addresses(departure_time_as_offset, packages_at_hub):
    packages_at_future_stops_view = [x for x in filter(lambda x: x.when_can_leave_hub_as_offset > departure_time_as_offset, packages_at_hub)]
    future_stops_street_addresses_set = set()
    for pkg in packages_at_future_stops_view:
        future_stops_street_addresses_set.add(pkg.street_address)
    return list(future_stops_street_addresses_set)



def new_pop2(departure_time_as_offset: int, packages_at_hub, truck_names):
    packages_at_hub = list(packages_at_hub) # make a copy
    
    # basic idea is to seed route1 and route2 with either:
    # - affinity rush pkgs in one, and farthest away rush package in the other
    # - faraway rush pkg in one, and farthest away rush pkg in the other
    # - faraway nonrush pkg in one, and farthest away nonrush pkg in the other
    # then we glom on additional packages in an order of priority according to which route they fit best into

    route1 = Route('route1', departure_time_as_offset)
    route1.truck_name = truck_names[0]
    route2 = Route('route2', departure_time_as_offset)
    route2.truck_name = truck_names[1]

    #
    # seed route1
    #
    rush_packages_ready_view, nonrush_packages_ready_view = update_rush_nonrush_packages_views(departure_time_as_offset, packages_at_hub)
    
    future_stops_street_addresses = update_future_stops_street_addresses(departure_time_as_offset, packages_at_hub)
    nonrush_packages_not_at_future_stops = list(filter(lambda pkg: pkg.street_address not in future_stops_street_addresses, nonrush_packages_ready_view))

    # I. if there are rush affinity packages, seed route1 with those packages
    p_ids_in_affinity = set()
    affinity_packages_are_rush = False
    for pkg in rush_packages_ready_view:
        if pkg.package_affinities != {0}:
            p_ids_in_affinity.add(pkg.id)
            p_ids_in_affinity.update(pkg.package_affinities)
            affinity_packages_are_rush = True
    for pkg in nonrush_packages_ready_view:
        if pkg.package_affinities != {0}:
            p_ids_in_affinity.add(pkg.id)
            p_ids_in_affinity.update(pkg.package_affinities)
    affinity_packages_ready = []
    for p_id in p_ids_in_affinity:
        cur_pkg = config.all_packages_by_id[p_id]
        affinity_packages_ready.append(cur_pkg)
        if cur_pkg in packages_at_hub:
            packages_at_hub.remove(cur_pkg)
    if affinity_packages_ready and affinity_packages_are_rush:
        for pkg in affinity_packages_ready:
            route1.load_package2(pkg, packages_at_hub)
    
    rush_packages_ready_view, nonrush_packages_ready_view = update_rush_nonrush_packages_views(departure_time_as_offset, packages_at_hub)

    # II. if there are no rush affinity packages but there are rush packages, populate route1 with the fartehest-away one
    if rush_packages_ready_view and not (affinity_packages_ready and affinity_packages_are_rush):
        rush_packages_ready_view.sort(key=lambda pkg: pkg.distance_from_hub, reverse=True)
        farthest_away_rush_package = rush_packages_ready_view[0]
        route1.load_package2(farthest_away_rush_package, packages_at_hub)

    # III. if there are no rush packages, populate route1 with farthest away nonrush package not at future stops
    nonrush_packages_not_at_future_stops = list(filter(lambda pkg: pkg.street_address not in future_stops_street_addresses, nonrush_packages_ready_view))
    if not rush_packages_ready_view and not (affinity_packages_ready and affinity_packages_are_rush):
        if nonrush_packages_not_at_future_stops:
            nonrush_packages_not_at_future_stops.sort(key=lambda pkg: pkg.distance_from_hub, reverse=True)
            route1.load_package2(nonrush_packages_not_at_future_stops[0], packages_at_hub)

    # IV. if we still haven't been able to populate route1 by this point, then return a pair of dummy routes that will be discarded
    if not route1.package_manifest:
        route1.distance_traveled_in_miles = float('inf')
        route2.distance_traveled_in_miles = float('inf')
        return ([route1, route2], [])

    #
    # seed route2
    #

    rush_packages_ready_view, nonrush_packages_ready_view = update_rush_nonrush_packages_views(departure_time_as_offset, packages_at_hub)
    nonrush_packages_not_at_future_stops = list(filter(lambda pkg: pkg.street_address not in future_stops_street_addresses, nonrush_packages_ready_view))

    # I. if there are still some rush packages, populate route2 with the one farthest away from route1
    route1_centroid = geo.get_centroid_of_objects(route1.package_manifest)
    if rush_packages_ready_view:
        rush_packages_ready_view.sort(key=lambda pkg: geo.haversine_distance(pkg.lat_long, route1_centroid), reverse=True)
        route2.load_package2(rush_packages_ready_view[0], packages_at_hub)
    
    # II. if there are no more rush packages, populate route2 with the farthest away nonrush not at future stops
    if not rush_packages_ready_view:
        pkgs_not_at_future_stops = list(filter(lambda pkg: pkg.street_address not in future_stops_street_addresses, nonrush_packages_ready_view))
        pkgs_not_at_future_stops.sort(key=lambda pkg: pkg.distance_from_hub, reverse=True)
        route2.load_package2(pkgs_not_at_future_stops[0], packages_at_hub)

    # III. if we still haven't been able to populate route1 by this point, then return a pair of dummy routes that will be discarded
    if not route1.package_manifest:
        route1.distance_traveled_in_miles = float('inf')
        route2.distance_traveled_in_miles = float('inf')
        return ([route1, route2], [])

        
    #
    # continue populating route1 and route2
    #

    # TODO: implement truck affinity group logic

    # add additional packages to route that suffers the least increase to their circuit length; stop adding packages if the miles per package increases past a certain amount

    rush_packages_ready_view, nonrush_packages_ready_view = update_rush_nonrush_packages_views(departure_time_as_offset, packages_at_hub)
    nonrush_packages_not_at_future_stops = list(filter(lambda pkg: pkg.street_address not in future_stops_street_addresses, nonrush_packages_ready_view))

    if rush_packages_ready_view:
        for pkg in rush_packages_ready_view:

            route1_dist_pre = route1.distance_traveled_in_miles
            route1.load_package2(pkg, packages_at_hub)
            route1_dist_delta = route1.distance_traveled_in_miles - route1_dist_pre
            route1.unload_package2(pkg, packages_at_hub)

            route2_dist_pre = route1.distance_traveled_in_miles
            route2.load_package2(pkg, packages_at_hub)
            route2_dist_delta = route2.distance_traveled_in_miles - route2_dist_pre
            route2.unload_package2(pkg, packages_at_hub)

            if route1_dist_delta < route2_dist_delta:
                if len(route1.package_manifest) < 16:
                    route1.load_package2(pkg, packages_at_hub)
            else:
                if len(route2.package_manifest) < 16:
                    route2.load_package2(pkg, packages_at_hub)

    rush_packages_ready_view, nonrush_packages_ready_view = update_rush_nonrush_packages_views(departure_time_as_offset, packages_at_hub)
    nonrush_packages_not_at_future_stops = list(filter(lambda pkg: pkg.street_address not in future_stops_street_addresses, nonrush_packages_ready_view))

    if nonrush_packages_not_at_future_stops:
        for pkg in nonrush_packages_not_at_future_stops:

            route1_dist_pre = route1.distance_traveled_in_miles
            route1.load_package2(pkg, packages_at_hub)
            route1_dist_delta = route1.distance_traveled_in_miles - route1_dist_pre
            route1.unload_package2(pkg, packages_at_hub)

            route2_dist_pre = route1.distance_traveled_in_miles
            route2.load_package2(pkg, packages_at_hub)
            route2_dist_delta = route2.distance_traveled_in_miles - route2_dist_pre
            route2.unload_package2(pkg, packages_at_hub)

            if route1_dist_delta < route2_dist_delta:
                if len(route1.package_manifest) < 16:
                    route1.load_package2(pkg, packages_at_hub)
            else:
                if len(route2.package_manifest) < 16:
                    route2.load_package2(pkg, packages_at_hub)

    return ([route1, route2], list(packages_at_hub))

def populate_two_routes(departure_time_as_offset: int, packages_at_hub, truck_names):

    rush_packages_ready = [x for x in filter(lambda x: x.deadline_as_offset < 1440 and x.when_can_leave_hub_as_offset <= departure_time_as_offset, packages_at_hub)]
    
    nonrush_packages_ready = [x for x in filter(lambda x: x.deadline_as_offset == 1440 and x.when_can_leave_hub_as_offset <= departure_time_as_offset, packages_at_hub)]

    seed_packages = []
    if rush_packages_ready:
        seed_packages += rush_packages_ready
    else:
        seed_packages += nonrush_packages_ready
        
    # pull out affinity group(s) from packages_at_hub
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

    # calculate centroid of affinity package stops
    affinity_packages_centroid = None # will initialize next
    if affinity_packages_ready:
        stops = my_package.convert_list_of_packages_to_stops(affinity_packages_ready)
        affinity_packages_centroid = geo.get_centroid_of_objects(stops)

    # calculate two sectors for remaining packages
    list_of_angles = get_angles_between_packages_sorted_greatest_to_least(packages_at_hub)
    route1_pkgs = []
    route2_pkgs = []
    for pkg in packages_at_hub:
        if geo.is_bearing_in_angle(pkg.bearing_from_hub, list_of_angles[0][2], list_of_angles[1][1]):
            route1_pkgs.append(pkg)
        else:
            route2_pkgs.append(pkg)

    # assign package affinity group to nearest sector
    if affinity_packages_ready:
        route1_centroid = geo.get_centroid_of_objects(route1_pkgs)
        route2_centroid = geo.get_centroid_of_objects(route2_pkgs)
        if geo.haversine_distance(route1_centroid, affinity_packages_centroid) < geo.haversine_distance(route2_centroid, affinity_packages_centroid):
            route1_pkgs += affinity_packages_ready
        else:
            route2_pkgs += affinity_packages_ready
    
    route1, pkgs_remaining1 = new_pop1(departure_time_as_offset, route1_pkgs, truck_names[0])
    route2, pkgs_remaining2 = new_pop1(departure_time_as_offset, route2_pkgs, truck_names[1])
    pkgs_remaining = []
    pkgs_remaining += pkgs_remaining1
    pkgs_remaining += pkgs_remaining2
    return ([route1, route2], pkgs_remaining)

