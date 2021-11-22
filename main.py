# {student_name: "Tim Stewart", student_id: "001476583"}

from functools import reduce
from operator import attrgetter, index

import geo
from geo import Stop
from geo import Route
import package
from package import Package
from truck import Truck
import config
import data
import my_time

if __name__ == '__main__':

    data.ingest_distances()
    data.ingest_packages()

    # 1. get all packages ready at 8 o'clock time
    ready_at_eight_oclock = package.retrieve_packages_ready_to_go('8:00 am')

    # 2. get subset that are rush packages
    eightoclock_rush_ids = [x for x in ready_at_eight_oclock if config.all_packages_by_id[x].deadline < 1440 or config.all_packages_by_id[x].package_affinities != {0}]

    # 3. add package affinities for the rush packages
    packages_in_affinity = set()
    for p_id in eightoclock_rush_ids:
        if config.all_packages_by_id[p_id].package_affinities != {0}:
            packages_in_affinity.update(config.all_packages_by_id[p_id].package_affinities)
    for p_id in packages_in_affinity:
        if p_id not in eightoclock_rush_ids:
            eightoclock_rush_ids.append(p_id)

    eight_oclock_rush_pkgs = []
    for p_id in eightoclock_rush_ids:
        eight_oclock_rush_pkgs.append(config.all_packages_by_id[p_id])

    # print(eight_oclock_rush_pkgs)

    eight_oclock_rush_pkgs.sort(key=lambda x:x.bearing_from_hub)
    earliest_bearing = eight_oclock_rush_pkgs[0].bearing_from_hub
    latest_bearing = eight_oclock_rush_pkgs[-1].bearing_from_hub
    list_of_angles = []
    for i, t in enumerate(eight_oclock_rush_pkgs):
        cur_bearing = t.bearing_from_hub
        next_bearing = -1 # will initialize in if/else block below
        if i + 1 == len(eight_oclock_rush_pkgs):
            next_bearing = eight_oclock_rush_pkgs[0].bearing_from_hub + 360
        else:
            next_bearing = eight_oclock_rush_pkgs[i+1].bearing_from_hub

        cur_diff = abs(next_bearing - cur_bearing)
        list_of_angles.append((cur_diff, cur_bearing, next_bearing))

    list_of_angles.sort(key=lambda x:x[0])
    list_of_angles.reverse()

    # print(list_of_angles)

    # populate our two package clusters
    cluster1_pkgs = []
    cluster2_pkgs = []
    for pkg in eight_oclock_rush_pkgs:
        if geo.is_bearing_in_angle(pkg.bearing_from_hub, list_of_angles[0][2], list_of_angles[1][1]):
            cluster1_pkgs.append(pkg)
        else:
            cluster2_pkgs.append(pkg)
    
    eight_oclock_route_1 = Route()

    # translate package clusters to lists of stops
    for street_address in set([x.street_address for x in cluster1_pkgs]):
        cur_stop = config.all_stops_by_street_address.get_or_default(street_address, '')
        if cur_stop not in eight_oclock_route_1.stops_not_yet_added_to_path:
            eight_oclock_route_1.stops_not_yet_added_to_path.append(cur_stop)

    # find weighted center of these stops
    sum_lat = 0.0
    sum_long = 0.0
    for stop in eight_oclock_route_1.stops_not_yet_added_to_path:
        sum_lat += stop.lat_long[0]
        sum_long += stop.lat_long[1]
    avg_lat = sum_lat / len(eight_oclock_route_1.stops_not_yet_added_to_path)
    avg_long = sum_long / len(eight_oclock_route_1.stops_not_yet_added_to_path)
    eight_oclock_route_1.weighted_center = (avg_lat, avg_long)

    eight_oclock_route_1.stops_not_yet_added_to_path.sort(key=lambda stop: geo.haversine_distance(eight_oclock_route_1.weighted_center, stop.lat_long), reverse=True)

    # for stop in eight_oclock_route_1.stops_not_yet_added_to_path:
    #     print(f"{stop.street_address}: {geo.haversine_distance(eight_oclock_route_1.weighted_center, stop.lat_long)}")


    # first, add stop farthest away from hub
    # then add stops on one side of this bearing, and then other side
    # on each side of the first bearing, add stops one at a time in order of decreasing distance from weighted center
    # insert each new stop between the two existing stops whose combined distance from the new stop is smaller than the combined distance of any other pair of adjacent existing stops

    eight_oclock_route_1.farthest_stop = eight_oclock_route_1.stops_not_yet_added_to_path[0]
    eight_oclock_route_1.path_to_farthest = [geo.HUB_STOP] + [eight_oclock_route_1.farthest_stop]
    eight_oclock_route_1.path_from_farthest = [eight_oclock_route_1.farthest_stop] + [geo.HUB_STOP]
    eight_oclock_route_1.stops_not_yet_added_to_path.remove(eight_oclock_route_1.farthest_stop)

    print(eight_oclock_route_1.stops_not_yet_added_to_path)

    
    # print(f"{eight_oclock_route_1.farthest_stop.bearing_from_hub}")
    for cur_stop in list(eight_oclock_route_1.stops_not_yet_added_to_path):
        # print(f"{geo.haversine_distance(eight_oclock_route_1.weighted_center, cur_stop.lat_long)}")

        # if  < eight_oclock_route_1.farthest_stop.bearing_from_hub:
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
            # print(f"bearing {cur_stop.bearing_from_hub} is late stop")
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

    # print(eight_oclock_route_1)
    print(my_time.convert_minutes_offset_to_time(config.MINUTES_PER_MILE * geo.distance_of_path_of_stops(eight_oclock_route_1.circuit)))


    exit()

    
    config.street_address_to_lat_long.get_or_default(b, '')

    # find the stop farthest from hub
    farthest_stop = [y[0] for y in sorted([(x, geo.get_distance(config.HUB_STREET_ADDRESS, x)) for x in cluster1_stops], key=lambda x:x[1], reverse=True)]

    
    route = [config.HUB_STREET_ADDRESS, farthest_stop, config.HUB_STREET_ADDRESS]

    





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