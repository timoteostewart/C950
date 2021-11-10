# {student_name: "Tim Stewart", student_id: "001476583"}

from operator import attrgetter

from package import Package
from truck import Truck

import config
import location
import my_time
import data

if __name__ == '__main__':

    
    data.ingest_distances()

    # for z in config.zips_from_west_to_east_rush:
    #     config.all_packages_by_zip[str(z)] = []
    
    data.ingest_packages()

    current_time = 0 # 8:00 am
    
    # load packages that have morning deadline
    rush_set_ids = set()
    nonrush_set_ids = set()

    # populate `rush_set_ids` with packages with morning deadlines _and_ with packages they have to be delivered with
    for p_id in config.hub_package_list:
        p = config.all_packages_by_id[p_id]
        if p.deadline < 1440 and p.when_can_leave_hub <= current_time:
            rush_set_ids.add(p_id)

            if p.package_affinities != {0}:
                for each_affinity_id in p.package_affinities:
                    rush_set_ids.add(each_affinity_id)
    
    # populate `nonrush_set_ids` with all the other packages
    for p_id in config.hub_package_list:
        if p_id not in rush_set_ids:
            nonrush_set_ids.add(p_id)

    
    truck1 = Truck('truck 1') # truck 1's first run leaves at 8:00 am
    for z in config.zips_from_west_to_east_rush:
        rush_pkgs_tuple = [(x, config.all_packages_by_id[x].street_address) for x in rush_set_ids if config.all_packages_by_id[x].zip == z]
        # sort packages on street address so that packages to same address are delivered at same time
        rush_pkgs_tuple.sort(key=lambda x:x[1])
        rush_pkgs_list = [x[0] for x in rush_pkgs_tuple]
        for p in rush_pkgs_list:
            truck1.add_package(p)
    print(f"{len(truck1.delivery_log)} {truck1.delivery_log}")
    truck1.end_run()

    truck2 = Truck('truck 2') # truck 2's first run leaves at 9:05 am
    truck2.start_time_this_run = '9:05 am'
    # load any delayed packages that are ready
    delayed_packages = [x for x in nonrush_set_ids if config.all_packages_by_id[x].when_can_leave_hub > my_time.convert_time_to_minutes_offset('8:00 am') and config.all_packages_by_id[x].when_can_leave_hub <= my_time.convert_time_to_minutes_offset('9:05 am')]
    for p in delayed_packages:
        truck2.add_package(p)
    # load any packages with an affinity to truck 2
    affinity_packages = [x for x in nonrush_set_ids if config.all_packages_by_id[x].truck_affinity == 'truck 2']
    # print(affinity_packages)
    for p in affinity_packages:
        truck2.add_package(p)
    
    print(f"{len(truck2.delivery_log)} {truck2.delivery_log}")
    truck2.end_run()
    
    # truck 1's second run leaves at 10:20 am
    truck1.start_time_this_run = '10:20 am'
    # load any delayed packages that are ready
    delayed_packages = [x for x in nonrush_set_ids if config.all_packages_by_id[x].when_can_leave_hub > my_time.convert_time_to_minutes_offset('9:06 am') and config.all_packages_by_id[x].when_can_leave_hub <= my_time.convert_time_to_minutes_offset('10:20 am')]
    # print(delayed_packages)
    for p in delayed_packages:
        truck1.add_package(p)
    
    # print(truck1.delivery_log)



    


    

    
    



        





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