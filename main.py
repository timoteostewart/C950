# {student_name: "Tim Stewart", student_id: "001476583"}

import math

import config
import data
import my_time
import route
from route import RouteList
from route import pop1_v3 as pop1_v3
from route import pop2_v4 as pop2_v4

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

    # update route_list's cumulative mileage
    cumulative_mileage = 0.0
    number_of_packages_delivered = 0
    for route in route_list.routes:
        if route.any_package_late:
            return # discard this route_list since it contains late package(s)
        cumulative_mileage += route.distance_traveled_in_miles
        number_of_packages_delivered += len(route.package_manifest)
    route_list.cumulative_mileage = cumulative_mileage
    route_list.number_of_packages_delivered = number_of_packages_delivered

    if route_list and route_list.cumulative_mileage > 140:
        return # discard this route_list
    
    if config.route_lists and route_list.cumulative_mileage > config.route_lists[0].cumulative_mileage:
        return # discard this route_list

    # see if we've taken too long
    if current_time_as_offset > 600:
        return # discard this route_list

    # see if we're out of packages
    if len(packages_at_hub) == 0:
        config.route_lists.append(route_list)
        config.route_lists.sort(key=lambda rl: rl.cumulative_mileage)
        return

    # compute truck_availability and related times_of_future_interest
    trucks_unavailable = []
    future_times_of_interest = []
    for cur_route in route_list.routes:
        if cur_route.return_time_as_offset > current_time_as_offset:
            trucks_unavailable.append(cur_route.truck_name)
            future_times_of_interest.append(cur_route.return_time_as_offset)
    # find remaining times_of_future_interest related to packages that arrive to hub late
    for pkg in packages_at_hub:
        if current_time_as_offset < pkg.when_can_leave_hub_as_offset:
            future_times_of_interest.append(pkg.when_can_leave_hub_as_offset)
    # if we have no future times of interest, set an arbitrary one 4 hours in the future
    if not future_times_of_interest:
        future_times_of_interest.append(current_time_as_offset + 240)
    # and finally, sort so we know the next soonest time of future interest
    future_times_of_interest.sort()
    
    # recursive cases
    # send zero trucks now (i.e., wait for next time of interest)
    if future_times_of_interest:
        rl = route_list.deep_copy()
        solver_helper(rl, future_times_of_interest[0], list(packages_at_hub))

    # send one truck now (truck 1)
    if 'truck 1' not in trucks_unavailable:
        result = pop1_v3(current_time_as_offset, list(packages_at_hub), 'truck 1')
        rl = route_list.deep_copy()
        rl.routes.append(result[0][0])
        solver_helper(rl, future_times_of_interest[0], list(result[1]))

    # send one truck now (truck 2)
    if 'truck 2' not in trucks_unavailable:
        result = pop1_v3(current_time_as_offset, list(packages_at_hub), 'truck 2')
        rl = route_list.deep_copy()
        rl.routes.append(result[0][0])
        solver_helper(rl, future_times_of_interest[0], list(result[1]))

    # # send two trucks now
    if not trucks_unavailable:
        # send them as truck 1 and truck 2
        result = pop2_v4(current_time_as_offset, list(packages_at_hub), ['truck 1', 'truck 2'])
        rl = route_list.deep_copy()
        if len(result[0]) == 1:
            rl.routes.append(result[0][0])
        else:
            rl.routes.append(result[0][0])
            rl.routes.append(result[0][1])
        solver_helper(rl, future_times_of_interest[0], list(result[1]))
        
        # send them as truck 2 and truck 1
        result = pop2_v4(current_time_as_offset, list(packages_at_hub), ['truck 2', 'truck 1'])
        rl = route_list.deep_copy()
        if len(result[0]) == 1:
            rl.routes.append(result[0][0])
        else:
            rl.routes.append(result[0][0])
            rl.routes.append(result[0][1])
        solver_helper(rl, future_times_of_interest[0], list(result[1]))
    

def print_delivery_schedule(route_list):
    if not route_list:
        print("This route_list is empty!")
        return
    
    for route in route_list.routes:
        cur_time = route.departure_time_as_offset
        for i, v in enumerate(route.ordered_list_of_stops):
            if i == 0:
                continue
            prev_stop = route.ordered_list_of_stops[i-1]
            cur_stop = route.ordered_list_of_stops[i]
            leg_distance = config.distances_between_pairs.get(f"{prev_stop.street_address} and {cur_stop.street_address}")
            leg_time = int(math.ceil(leg_distance * config.MINUTES_PER_MILE)) # round time up to next minute
            cur_time += leg_time
            for pkg in route.package_manifest:
                if pkg.street_address == cur_stop.street_address:
                    if pkg.deadline_as_offset == 1440:
                        print(f"{route.truck_name} delivered nonrush package {pkg.id} at {my_time.convert_minutes_offset_to_time(cur_time)}", end='')
                    else:
                        print(f"{route.truck_name} delivered    rush package {pkg.id} at {my_time.convert_minutes_offset_to_time(cur_time)} (deadline is {my_time.convert_minutes_offset_to_time(pkg.deadline_as_offset)})", end='')
                    if pkg.truck_affinity:
                        print(f"                        (affinity {pkg.truck_affinity})")
                    else:
                        print("")


if __name__ == '__main__':
    data.ingest_distances()
    packages_at_hub = data.ingest_packages()

    winner = solver('8:00 am', list(packages_at_hub))
    
    if winner:
        print(f"traveled {winner.cumulative_mileage} miles and delivered {winner.number_of_packages_delivered} packages")
        for route in winner.routes:
            print(f"{route}, packages: ", end='')
            route.convert_ordered_list_of_stops_to_package_delivery_order()
            # print("")

    print_delivery_schedule(winner)
