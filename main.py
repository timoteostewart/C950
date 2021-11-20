# {student_name: "Tim Stewart", student_id: "001476583"}

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

    print(list_of_angles)


    # populate our two clusters
    cluster1 = []
    cluster2 = []
    for pkg in eight_oclock_rush_pkgs:
        if geo.is_bearing_in_angle(pkg.bearing_from_hub, list_of_angles[0][2], list_of_angles[1][1]):
            cluster1.append(pkg)
        else:
            cluster2.append(pkg)
        
    
    for x in cluster1:
        print(f"{x.id} {x.bearing_from_hub}")

    # reorder cluster1 in clockwise bearing order
    # find first location
    for i, v in enumerate(cluster1):
        if v.bearing_from_hub == list_of_angles[0][2]:
            cluster1 = cluster1[slice(i, len(cluster1))] + cluster1[slice(0, i)]
            break
    
    print("-----")
    for x in cluster1:
        print(f"{x.id} {x.bearing_from_hub}")
    
    





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