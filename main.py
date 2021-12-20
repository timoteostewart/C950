# {student_name: "Tim Stewart", student_id: "001476583"}

import math

import config
import data
from delivery_schedule_writer import DeliveryScheduleWriter
import geo
import my_time
import route
import snapshot

from album import Album
from interface import user_interface as user_interface
from route import RouteList
from route import populate_1_route as populate_1_route
from route import populate_2_routes as populate_2_routes
from snapshot import Snapshot
from truck import Truck

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
        # TODO: when closing out a route list, add the starting and ending times as offsets
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
    

def store_snapshot_to_master_delivery_log(cur_time, route):
    pass



if __name__ == '__main__':

    data.ingest_distances()
    packages_at_hub = data.ingest_packages()

    # s = Snapshot(-1)
    # # initialize package statuses
    # for p_id in range(1, 41):
    #     s.package_statuses[p_id] = config.all_packages_by_id_ht.get(p_id).delivery_status
    # s.update_computed_values(packages_at_hub)
    # s.display()

    # user_interface()

    # exit()

    data.ingest_distances()
    packages_at_hub = data.ingest_packages()

    winner = solver('8:00 am', list(packages_at_hub))
    
    if winner:
        print(f"traveled {winner.cumulative_mileage} miles and delivered {winner.number_of_packages_delivered} packages")
        for route in winner.routes:
            print(f"{route}, packages: ", end='')
            route.convert_ordered_list_of_stops_to_package_delivery_order()
            # print("")
        
        print("press any key to inspect the delivery schedule more closely")

        dsw = DeliveryScheduleWriter(winner)
        album = dsw.populate_album_with_snapshots()
        album.display_active_snapshots()


    else:
        print("This is very embarrassing, but no solution could be found!")
