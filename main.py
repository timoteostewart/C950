# {student_name: "Tim Stewart", student_id: "001476583"}

from copy import copy
from copy import deepcopy
from functools import reduce
from operator import attrgetter, index
from os import closerange

import config
import data
import geo
import my_package
import my_time
import route
from route import RouteList, new_pop1 as new_pop1
from route import populate_two_routes as populate_two_routes
from route import new_pop2 as new_pop2
import truck

def solver(first_departure_time, packages_at_hub):
    empty_route_list = RouteList()
    solver_helper(empty_route_list, my_time.convert_time_to_minutes_offset(first_departure_time), list(packages_at_hub))
    print(f"found {len(config.route_lists)} routes")
    config.route_lists.sort(key=lambda route_list: route_list.cumulative_mileage)
    if config.route_lists:
        return config.route_lists[0]
    else:
        return None


def solver_helper(route_list, current_time_as_offset, packages_at_hub):

    # base case; guard clauses
    # calculate route_list's cumulative mileage
    cumulative_mileage = 0.0
    number_of_packages_delivered = 0
    for route in route_list.routes:
        cumulative_mileage += route.distance_traveled_in_miles
        number_of_packages_delivered += len(route.package_manifest)
    route_list.cumulative_mileage = cumulative_mileage
    route_list.number_of_packages_delivered = number_of_packages_delivered

    if route_list.cumulative_mileage > 250:
        config.failed_route_lists += 1
        return # discard this route_list
    
    # see if we've taken more than 8 hours:
    if current_time_as_offset > 480:
        config.failed_route_lists += 1
        return # discard this route_list

    print(f"entered solver helper with mileage {route_list.cumulative_mileage} and packages {len(packages_at_hub)}")

    route_list_copy = route_list.deep_copy()
    packages_at_hub_copy = list(packages_at_hub)

    # see if we're out of packages
    if len(packages_at_hub) == 0:
        config.route_lists.append(route_list)
        return

    # compute truck_availability and some times_of_future_interest
    trucks_unavailable = []
    future_times_of_interest = []
    if len(route_list_copy.routes) >= 2:
        for offset in [-1, -2]:
            cur_route = route_list_copy.routes[offset]
            if cur_route.return_time_as_offset > current_time_as_offset:
                trucks_unavailable.append(cur_route.truck_name)
                future_times_of_interest.append(cur_route.return_time_as_offset)
    elif len(route_list_copy.routes) == 1:
        cur_route = route_list_copy.routes[-1]
        if cur_route.return_time_as_offset > current_time_as_offset:
            trucks_unavailable.append(cur_route.truck_name)
            future_times_of_interest.append(cur_route.return_time_as_offset)

    # find remaining times_of_future_interest and sort them
    for pkg in packages_at_hub:
        if pkg.when_can_leave_hub_as_offset > current_time_as_offset:
            future_times_of_interest.append(pkg.when_can_leave_hub_as_offset)
    future_times_of_interest.sort()

    if not future_times_of_interest: # if we have no future times of interest, set an arbitrary one 4 hours in the future
        future_times_of_interest = [current_time_as_offset + 240]
    
    # recursive cases
    # send zero trucks now (i.e., wait for next time of interest)
    if future_times_of_interest:
        solver_helper(route_list_copy, future_times_of_interest[0], packages_at_hub_copy)

    # send one truck now (truck 1)
    if 'truck 1' not in trucks_unavailable:
        result = new_pop1(current_time_as_offset, packages_at_hub_copy, 'truck 1')
        rl = route_list.deep_copy()
        rl.routes.append(result[0])
        solver_helper(rl, future_times_of_interest[0], list(result[1]))

    # send one truck now (truck 2)
    if 'truck 2' not in trucks_unavailable:
        result = new_pop1(current_time_as_offset, packages_at_hub_copy, 'truck 2')
        rl = route_list.deep_copy()
        rl.routes.append(result[0])
        solver_helper(rl, future_times_of_interest[0], list(result[1]))

    # send two trucks now
    if not trucks_unavailable and len(packages_at_hub) > 1:
        # send them as truck 1 and truck 2
        result = new_pop2(current_time_as_offset, packages_at_hub_copy, ['truck 1', 'truck 2'])
        rl = route_list.deep_copy()
        rl.routes.append(result[0][0])
        rl.routes.append(result[0][1])
        solver_helper(rl, future_times_of_interest[0], list(result[1]))
        
        # send them as truck 2 and truck 1
        result = new_pop2(current_time_as_offset, packages_at_hub_copy, ['truck 2', 'truck 1'])
        rl = route_list.deep_copy()
        rl.routes.append(result[0][0])
        rl.routes.append(result[0][1])
        solver_helper(rl, future_times_of_interest[0], list(result[1]))
    




if __name__ == '__main__':

    data.ingest_distances()
    data.ingest_packages()

    winner = solver('8:00 am', list(config.packages_at_hub))
    if winner:
        print(f"traveled {winner.cumulative_mileage} miles and delivered {winner.number_of_packages_delivered} packages")
        for route in winner.routes:
            print(route)
    
    print(f"{config.failed_route_lists} failed routes")

    # pkgs_remaining = config.packages_at_hub

    # first_route, pkgs_remaining = route.populate_one_route(0, pkgs_remaining, 'truck 2')
    # if route.validate_route(first_route):
    #     config.cumulative_miles += first_route.distance_traveled_in_miles

    # second_route, pkgs_remaining = route.populate_one_route(65, pkgs_remaining, 'truck 2')
    # if route.validate_route(second_route):
    #     config.cumulative_miles += second_route.distance_traveled_in_miles

    # third_route, pkgs_remaining = route.populate_one_route(140, pkgs_remaining, 'truck 2')
    # if route.validate_route(third_route):
    #     config.cumulative_miles += third_route.distance_traveled_in_miles

    # fourth_route, pkgs_remaining = route.populate_one_route(140, pkgs_remaining, 'truck 2')
    # if route.validate_route(fourth_route):
    #     config.cumulative_miles += fourth_route.distance_traveled_in_miles

    # print(config.cumulative_miles)
    # exit()

    