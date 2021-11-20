# {student_name: "Tim Stewart", student_id: "001476583"}

from functools import reduce
from operator import attrgetter

from package import Package
from geo import Destination
import package
from truck import Truck

import config
import geo
import my_time
import data

if __name__ == '__main__':

    data.ingest_distances()
    data.ingest_packages()
    
    # 1. get all packages ready at this time
    ready_at_eight_oclock = package.retrieve_packages_ready_to_go('8:00 am')

    # 2. get subset that are rush packages
    eightoclock_rush_ids = [x for x in ready_at_eight_oclock if config.all_packages_by_id[x].deadline < 1440 or config.all_packages_by_id[x].package_affinities != {0}]

    # 3. add package affinities
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
        
    # translate package clusters to lists of stops
    cluster1_stops = []
    for pkg in cluster1_pkgs:
        if pkg.street_address not in cluster1_stops:
            cluster1_stops.append(pkg.street_address)

    # find weighted center of these stops
    sum_lat = 0.0
    sum_long = 0.0
    for x in cluster1_stops:
        sum_lat += geo.street_address_to_lat_long.get_or_default(x, '')[0]
        sum_long += geo.street_address_to_lat_long.get_or_default(x, '')[1]
    avg_lat = sum_lat / len(cluster1_stops)
    avg_long = sum_long / len(cluster1_stops)

    print((avg_lat, avg_long))

    for x in cluster1_stops:
        weighted_center = (avg_lat, avg_long)
        cur_stop = geo.street_address_to_lat_long.get_or_default(x, '')
        print(f"{x}: {geo.haversine_distance(weighted_center , cur_stop)}")


    # TODO: add stops one at a time in order of decreasing distance from weighted center
    # insert each new stop between the two existing stops whose combined distance from the new stop is smaller than the combined distance of any other pair of adjacent existing stops

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