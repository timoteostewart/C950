from dataclasses import dataclass
import math

import config
import geo
import my_time

class Route:
    def __init__(self, name, departure_time_as_offset):
        self.name = name
        self.truck_name = ''
        self.departure_time_as_offset = departure_time_as_offset

        self.packages_at_hub = []
        self.package_manifest = []
        self.ordered_list_of_stops = []

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
        new_route.distance_traveled_in_miles = self.distance_traveled_in_miles
        new_route.departure_time_as_offset = self.departure_time_as_offset
        new_route.return_time_as_offset = self.return_time_as_offset
        return new_route


    def load_package(self, pkg, packages_at_hub):
        if pkg not in self.package_manifest:
            self.package_manifest.append(pkg)
        if pkg in packages_at_hub:
            packages_at_hub.remove(pkg)
        self.create_ordered_list_of_stops()
        self.update_route_stats()


    def unload_package(self, pkg, packages_at_hub):
        if pkg in self.package_manifest:
            self.package_manifest.remove(pkg)
        if pkg not in packages_at_hub:
            packages_at_hub.append(pkg)
        if len(self.package_manifest) > 0:
            self.create_ordered_list_of_stops()
        self.update_route_stats()


    def create_ordered_list_of_stops(self):
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

        # to be updated:    self.any_package_late: bool
        #                   self.distance_traveled_in_miles: float
        #                   self.return_time_as_offset: int
        
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


def update_rush_nonrush_packages_views(departure_time_as_offset, packages_at_hub):
    packages_at_future_stops = list(filter(lambda pkg: departure_time_as_offset < pkg.when_can_leave_hub_as_offset, packages_at_hub))
    future_stops_street_addresses_set = set()
    for pkg in packages_at_future_stops:
        future_stops_street_addresses_set.add(pkg.street_address)
    
    eligible_rush_packages = [pkg for pkg in filter(lambda pkg: pkg.deadline_as_offset < 1440 and pkg.when_can_leave_hub_as_offset <= departure_time_as_offset, packages_at_hub)]
    
    eligible_nonrush_packages = [pkg for pkg in filter(lambda pkg: pkg.deadline_as_offset == 1440 and pkg.when_can_leave_hub_as_offset <= departure_time_as_offset and pkg.street_address not in future_stops_street_addresses_set, packages_at_hub)]

    return eligible_rush_packages, eligible_nonrush_packages


def update_package_affinity_packages_view(packages_at_hub):
    p_ids_in_affinity = set()
    for pkg in packages_at_hub:
        if pkg.package_affinities != {0}:
            p_ids_in_affinity.add(pkg.id)
            p_ids_in_affinity.update(pkg.package_affinities)
    affinity_packages_view = []
    for p_id in p_ids_in_affinity:
        cur_package = config.all_packages_by_id[p_id]
        affinity_packages_view.append(cur_package)
    return affinity_packages_view


def populate_1_route(departure_time_as_offset: int, packages_at_hub, truck_name):
    packages_at_hub = list(packages_at_hub) # make a copy

    route1 = Route('route1', departure_time_as_offset)
    route1.truck_name = truck_name

    # identify eligible packages
    eligible_rush_packages, eligible_nonrush_packages = update_rush_nonrush_packages_views(departure_time_as_offset, packages_at_hub)
    # sort packages_at_hub by soonest due, then by distance from hub
    eligible_rush_packages.sort(key=lambda pkg: pkg.when_can_leave_hub_as_offset * 100 + pkg.distance_from_hub)
    eligible_nonrush_packages.sort(key=lambda pkg: pkg.when_can_leave_hub_as_offset * 100 + pkg.distance_from_hub)
    affinity_packages_view = update_package_affinity_packages_view(packages_at_hub)

    # load rush packages
    while eligible_rush_packages and len(route1.package_manifest) < 16:
        cur_pkg = eligible_rush_packages.pop(0)
        if cur_pkg.truck_affinity and cur_pkg.truck_affinity != truck_name:
            continue
        route1.load_package(cur_pkg, packages_at_hub)
        if route1.any_package_late:
            route1.unload_package(cur_pkg, packages_at_hub)
            break
        
        # handler for packages that must be delivered with other packages
        # (i.e., handler for packages in affinity with each other)
        if cur_pkg in affinity_packages_view:
            for pkg in affinity_packages_view:
                if pkg not in route1.package_manifest:
                    route1.load_package(pkg, packages_at_hub)

    # load nonrush packages
    while eligible_nonrush_packages and len(route1.package_manifest) < 16:
        cur_pkg = eligible_nonrush_packages.pop(0)
        if cur_pkg.truck_affinity and cur_pkg.truck_affinity != truck_name:
            continue
        route1.load_package(cur_pkg, packages_at_hub)
        if route1.any_package_late:
            route1.unload_package(cur_pkg, packages_at_hub)
            break

    return ([route1], packages_at_hub)


def populate_2_routes(departure_time_as_offset: int, packages_at_hub, truck_names):
    packages_at_hub = list(packages_at_hub) # make a copy

    route1 = Route('route1', departure_time_as_offset)
    route1.truck_name = truck_names[0]

    route2 = Route('route2', departure_time_as_offset)
    route2.truck_name = truck_names[1]

    # if just one package, then populate one route with it and return that result
    if len(packages_at_hub) == 1:
        result = populate_1_route(departure_time_as_offset, list(packages_at_hub), 'truck 2')
        return ([result[0][0]],  list(result[1]))

    # identify eligible packages
    eligible_rush_packages, eligible_nonrush_packages = update_rush_nonrush_packages_views(departure_time_as_offset, packages_at_hub)
    # sort packages_at_hub by soonest due, then by distance from hub
    eligible_rush_packages.sort(key=lambda pkg: pkg.when_can_leave_hub_as_offset * 100 + pkg.distance_from_hub)
    eligible_nonrush_packages.sort(key=lambda pkg: pkg.when_can_leave_hub_as_offset * 100 + pkg.distance_from_hub)
    affinity_packages_view = update_package_affinity_packages_view(packages_at_hub)

    # load route1 rush
    while eligible_rush_packages and len(route1.package_manifest) < 16:
        cur_pkg = eligible_rush_packages.pop(0)
        if cur_pkg.truck_affinity and cur_pkg.truck_affinity != route1.truck_name:
            continue
        route1.load_package(cur_pkg, packages_at_hub)
        if route1.any_package_late:
            route1.unload_package(cur_pkg, packages_at_hub)
            break

        # handler for packages that must be delivered with other packages
        # (i.e., handler for packages in affinity with each other)
        if cur_pkg in affinity_packages_view:
            for pkg in affinity_packages_view:
                if pkg not in route1.package_manifest:
                    route1.load_package(pkg, packages_at_hub)

    # load route1 nonrush
    while eligible_nonrush_packages and len(route1.package_manifest) < 16:
        cur_pkg = eligible_nonrush_packages.pop(0)
        if cur_pkg.truck_affinity and cur_pkg.truck_affinity != route1.truck_name:
            continue
        route1.load_package(cur_pkg, packages_at_hub)
        if route1.any_package_late:
            route1.unload_package(cur_pkg, packages_at_hub)
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
        route2.load_package(cur_pkg, packages_at_hub)
        if route2.any_package_late:
            route2.unload_package(cur_pkg, packages_at_hub)
            break

    # load route2 nonrush
    while eligible_nonrush_packages and len(route2.package_manifest) < 16:
        cur_pkg = eligible_nonrush_packages.pop(0)
        if cur_pkg.truck_affinity and cur_pkg.truck_affinity != route2.truck_name:
            continue
        route2.load_package(cur_pkg, packages_at_hub)
        if route2.any_package_late:
            route2.unload_package(cur_pkg, packages_at_hub)
            break

    return ([route1, route2], packages_at_hub)
