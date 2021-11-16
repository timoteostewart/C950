# {student_name: "Tim Stewart", student_id: "001476583"}

from operator import attrgetter

from package import Package
import package
from truck import Truck

import config
import location
import my_time
import data

if __name__ == '__main__':

    data.ingest_distances()
    data.ingest_packages()


    ready_at_eight_oclock = package.retrieve_packages_ready_to_go('8:00 am')

    eightoclock_rush = [x for x in ready_at_eight_oclock if config.all_packages_by_id[x].deadline < 1440 or config.all_packages_by_id[x].package_affinities != {0}]
    packages_in_affinity = set()
    for p in eightoclock_rush:
        if config.all_packages_by_id[p].package_affinities != {0}:
            packages_in_affinity.update(config.all_packages_by_id[p].package_affinities)
    for p in packages_in_affinity:
        if p not in eightoclock_rush:
            eightoclock_rush.append(p)

    eight_rush_sorted_greedy = []
    cur_location = config.HUB_STREET_ADDRESS
    while eightoclock_rush:
        cur_least_distance = 0.0
        cur_closest_location = ''
        cur_closest_p_id = 0
        for p_id in eightoclock_rush:
            cur_distance = data.get_distance(cur_location, config.all_packages_by_id[p_id].street_address)
            if cur_distance < cur_least_distance:
                cur_least_distance = cur_distance
                cur_closest_location = config.all_packages_by_id[p_id].street_address
                cur_closest_p_id = p_id
        eight_rush_sorted_greedy.append(p_id)
        eightoclock_rush.remove(p_id)

    # southeast route
    truck1 = Truck('truck 1') # truck 2's first run leaves at 8:00 am
    truck1.add_packages([14, 15, 16, 34, 22, 26, 24, 18, 11, 23, 12, 36, 17]) # 15 is 9am deadline
    truck1.end_run()
    
    # north route
    truck2 = Truck('truck 2') # truck 1's first run leaves at 8:00 am
    truck2.add_packages([20, 19, 31, 40, 4, 1, 27, 39, 13, 30, 8, 5, 37, 10, 29])
    # truck1.add_packages(eight_rush_sorted_greedy) # [19, 40, 37, 34, 31, 30, 29, 20, 16, 15, 14, 13, 1]
    truck2.end_run()

    

    # delayed till 9:05 am: 6, 25, 28, 32
    # delayed till 10:20 am: 9



    # truck 1's 2nd run
    truck1.add_packages([21, 32, 35, 38, 33, 28])
    truck1.end_run()

    # truck 2's 2nd run
    # truck 2: 3, 18, 36, 38
    truck2.add_packages([2, 3, 6, 7, 25])
    truck2.end_run()

    truck2.add_packages([9])
    truck2.end_run()

    print(config.hub_stats_miles)
    print(f"packages not delivered: {config.hub_package_list}")



    


    

    
    



        





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