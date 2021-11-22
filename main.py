# {student_name: "Tim Stewart", student_id: "001476583"}

from functools import reduce
from operator import attrgetter, index

import geo
from geo import Stop
import package
from package import Package
from route import Route
from truck import Truck
import config
import data
import my_time

if __name__ == '__main__':

    data.ingest_distances()
    data.ingest_packages()

    # 1. get all packages ready at 8 o'clock time
    pkgs_eight_oclock_all = [x for x in filter(lambda x: x.when_can_leave_hub == my_time.convert_time_to_minutes_offset('8:00 am'), config.packages_at_hub)]

    # 2. get subset that are rush packages
    pkgs_eight_oclock_rush = [x for x in filter(lambda x: x.deadline < 1440 and x.when_can_leave_hub == my_time.convert_time_to_minutes_offset('8:00 am'), config.packages_at_hub)]
    
    # 3. add package affinities for the rush packages
    ids_of_packages_in_affinity = set()
    for pkg in pkgs_eight_oclock_rush:
        if pkg.package_affinities != {0}:
            ids_of_packages_in_affinity.update(pkg.package_affinities)
    for p_id in ids_of_packages_in_affinity:
        if config.all_packages_by_id[p_id] not in pkgs_eight_oclock_rush:
            pkgs_eight_oclock_rush.append(config.all_packages_by_id[p_id])

    # 4. group packages into clusters
    pkgs_eight_oclock_rush.sort(key=lambda x:x.bearing_from_hub)
    earliest_bearing = pkgs_eight_oclock_rush[0].bearing_from_hub
    latest_bearing = pkgs_eight_oclock_rush[-1].bearing_from_hub
    list_of_angles = []
    for i, t in enumerate(pkgs_eight_oclock_rush):
        cur_bearing = t.bearing_from_hub
        next_bearing = -1 # will initialize in if/else block below
        if i + 1 == len(pkgs_eight_oclock_rush):
            next_bearing = pkgs_eight_oclock_rush[0].bearing_from_hub + 360
        else:
            next_bearing = pkgs_eight_oclock_rush[i+1].bearing_from_hub

        cur_diff = abs(next_bearing - cur_bearing)
        list_of_angles.append((cur_diff, cur_bearing, next_bearing))

    list_of_angles.sort(key=lambda x:x[0])
    list_of_angles.reverse()

    # populate our two package clusters
    eight_oclock_route_1 = Route()
    eight_oclock_route_2 = Route()
    for pkg in pkgs_eight_oclock_rush:
        if geo.is_bearing_in_angle(pkg.bearing_from_hub, list_of_angles[0][2], list_of_angles[1][1]):
            eight_oclock_route_1.manifest_required_packages.append(pkg)
        else:
            eight_oclock_route_2.manifest_required_packages.append(pkg)

    # add additional packages that are ready and are going to the same place as an existing package
    existing_addresses = {x.street_address for x in eight_oclock_route_1.manifest_required_packages}
    for pkg in pkgs_eight_oclock_all:
        if pkg not in eight_oclock_route_1.manifest_required_packages and pkg not in eight_oclock_route_1.manifest_optional_packages:
            if pkg.street_address in existing_addresses:
                print(f"pkg id {pkg.id} going to same address as existing package")
                eight_oclock_route_1.manifest_optional_packages.append(pkg)
    
    eight_oclock_route_1.manifest_all_packages = eight_oclock_route_1.manifest_required_packages + eight_oclock_route_1.manifest_optional_packages
    
    # translate package clusters to lists of stops
    for street_address in set([x.street_address for x in eight_oclock_route_1.manifest_all_packages]):
        cur_stop = config.all_stops_by_street_address.get_or_default(street_address, '')
        if cur_stop not in eight_oclock_route_1.stops_not_yet_added_to_path:
            eight_oclock_route_1.stops_not_yet_added_to_path.append(cur_stop)

    eight_oclock_route_1.update_weighted_center()

    # first, add stop farthest away from hub
    # then add stops on one side of this bearing, and then other side
    # on each side of the first bearing, add stops one at a time in order of decreasing distance from weighted center
    # insert each new stop between the two existing stops whose combined distance from the new stop is smaller than the combined distance of any other pair of adjacent existing stops

    eight_oclock_route_1.update_farthest_stop()

    # insert stops into the two paths that will later be joined to make a circuit.
    # one path goes from hub to farthest stop; the other path goes from farthest stop to hub.
    # movement on the circuit will be more or less clockwise.
    for cur_stop in list(eight_oclock_route_1.stops_not_yet_added_to_path):
        if geo.is_bearing_in_angle(cur_stop.bearing_from_hub, eight_oclock_route_1.earliest_bearing, eight_oclock_route_1.farthest_stop.bearing_from_hub):
            cur_least_distance = float('inf')
            index_insert_after = -1
            for i in range(0, len(eight_oclock_route_1.path_to_farthest) - 1):
                cur_distance = geo.distance_of_path_of_stops([eight_oclock_route_1.path_to_farthest[i]] + [cur_stop] + [eight_oclock_route_1.path_to_farthest[i+1]])
                if cur_distance < cur_least_distance:
                    cur_least_distance = cur_distance
                    index_insert_after = i
            eight_oclock_route_1.path_to_farthest.insert(i + 1, cur_stop)
        else:
            cur_least_distance = float('inf')
            index_insert_after = -1
            for i in range(0, len(eight_oclock_route_1.path_from_farthest) - 1):
                cur_distance = geo.distance_of_path_of_stops([eight_oclock_route_1.path_from_farthest[i]] + [cur_stop] + [eight_oclock_route_1.path_from_farthest[i+1]])
                if cur_distance < cur_least_distance:
                    cur_least_distance = cur_distance
                    index_insert_after = i
            eight_oclock_route_1.path_from_farthest.insert(i + 1, cur_stop)

        eight_oclock_route_1.stops_not_yet_added_to_path.remove(cur_stop)
    
    eight_oclock_route_1.circuit = eight_oclock_route_1.path_to_farthest + eight_oclock_route_1.path_from_farthest[1:]

    print(eight_oclock_route_1)
    print(my_time.convert_minutes_offset_to_time(config.MINUTES_PER_MILE * geo.distance_of_path_of_stops(eight_oclock_route_1.circuit)))
    
    # add additional packages 
    # 1. make list of packages that could be delivered
    optional_packages = []
    # for 

    exit()






    # # north route
    # truck2 = Truck('truck 2') # truck 2's first run leaves at 8:00 am
    # truck2.add_packages([20, 19, 31, 40, 1, 13, 37, 30, 29])
    # truck2.end_run()
    
    # # southeast route
    # truck1 = Truck('truck 1') # truck 1's first run leaves at 8:00 am
    # truck1.add_packages([13, 14, 15, 16, 34, 19, 20]) # 15 is 9am deadline
    # truck1.end_run()
    
    # # delayed till 9:05 am: 6, 25, 28, 32
    # # delayed till 10:20 am: 9

    # # truck 1's 2nd run
    # truck1.add_packages([21, 32, 35, 38, 33, 28])
    # truck1.end_run()

    # # truck 2's 2nd run
    # # affinity with truck 2:  3, 18, 36, 38
    # truck2.add_packages([2, 3, 6, 7, 25])
    # truck2.end_run()

    # truck2.add_packages([9])
    # truck2.end_run()

    # print(config.hub_stats_miles)
    # print(f"packages not delivered: {config.hub_package_list}")



    


    

    
    



        





    # timeline of special events:
    # at 8:00 am: packages that are ready may leave hub
    # at 9:05 am: packages 6, 25, 28, 32 arrive at hub and are ready to go
    # at 10:20 am: package 9 gets corrected address and is ready to go
    # EOD (end of day): when all packages are delivered
    # goal: max of _140 miles_ traveled by both trucks
    # program flow:
    # ingest packages
    # load trucks
    # send trucks out
    # reload trucks
    # repeat till done