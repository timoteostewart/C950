# {student_name: "Tim Stewart", student_id: "001476583"}

import config
import data
from delivery_schedule_writer import DeliveryScheduleWriter
import my_time
import route

from interface import user_interface as user_interface
from route import RouteList
from route import populate_1_route as populate_1_route
from route import populate_2_routes as populate_2_routes
 

def solver(first_departure_time, packages_at_hub):
    empty_route_list = RouteList()
    solver_helper(empty_route_list, my_time.convert_time_to_minutes_offset(first_departure_time), list(packages_at_hub))
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
        result = populate_1_route(current_time_as_offset, list(packages_at_hub), 'truck 1')
        rl = route_list.deep_copy()
        rl.routes.append(result[0][0])
        solver_helper(rl, future_times_of_interest[0], list(result[1]))

    # send one truck now (truck 2)
    if 'truck 2' not in trucks_unavailable:
        result = populate_1_route(current_time_as_offset, list(packages_at_hub), 'truck 2')
        rl = route_list.deep_copy()
        rl.routes.append(result[0][0])
        solver_helper(rl, future_times_of_interest[0], list(result[1]))

    # # send two trucks now
    if not trucks_unavailable:
        # send them as truck 1 and truck 2
        result = populate_2_routes(current_time_as_offset, list(packages_at_hub), ['truck 1', 'truck 2'])
        rl = route_list.deep_copy()
        if len(result[0]) == 1:
            rl.routes.append(result[0][0])
        else:
            rl.routes.append(result[0][0])
            rl.routes.append(result[0][1])
        solver_helper(rl, future_times_of_interest[0], list(result[1]))
        
        # send them as truck 2 and truck 1
        result = populate_2_routes(current_time_as_offset, list(packages_at_hub), ['truck 2', 'truck 1'])
        rl = route_list.deep_copy()
        if len(result[0]) == 1:
            rl.routes.append(result[0][0])
        else:
            rl.routes.append(result[0][0])
            rl.routes.append(result[0][1])
        solver_helper(rl, future_times_of_interest[0], list(result[1]))
    

if __name__ == '__main__':

    data.ingest_distances()
    packages_at_hub = data.ingest_packages()

    winner = solver('8:00 am', list(packages_at_hub))
    
    if config.route_lists:
        print(f"The back-tracking plus heuristics algorithm found {len(config.route_lists)} valid ways to solve the problem.\n"
        f"The winning set of {len(winner.routes)} routes traveled a total of {winner.cumulative_mileage} miles and delivered {winner.number_of_packages_delivered} packages with no missed deadlines and all package constraints met.\n"
        f"Here are the routes with their truck numbers and details:"
        f"")
        for route in winner.routes:
            print(f"{route} Packages delivered: {route.convert_ordered_list_of_stops_to_package_delivery_order()}")
            
        dsw = DeliveryScheduleWriter(winner)
        album = dsw.populate_album_with_snapshots()
        user_interface(album)
    else:
        print("This is very embarrassing, but no solution to the Vehicle Routing Problem (VRP) could be found!")
