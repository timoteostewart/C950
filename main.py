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
    data.ingest_packages()

    # populate `rush_set_ids` with packages with morning deadlines _and_ with packages they have to be delivered with
    rush_ready_at_800am_ids = set()
    rush_ready_at_905am_ids = set()
    for p_id in config.hub_package_list:
        p = config.all_packages_by_id[p_id]
        if p.deadline < 1440:
            if p.when_can_leave_hub == 0:
                rush_ready_at_800am_ids.add(p_id)
                if p.package_affinities != {0}:
                    for each_affinity_id in p.package_affinities:
                        rush_ready_at_800am_ids.add(each_affinity_id)
            elif p.when_can_leave_hub == 65:
                rush_ready_at_905am_ids.add(p_id)
                if p.package_affinities != {0}:
                    for each_affinity_id in p.package_affinities:
                        rush_ready_at_905am_ids.add(each_affinity_id)

    truck1 = Truck('truck 1') # truck 1's first run leaves at 8:00 am
    # special features of this run:
    #  - rush packages (morning deadline): #1, #13, #14, #15, #16, #20, #29, #30, #31, #34, #37, #40
    #  - packages with package affinities: #19
    for z in config.zips_from_west_to_east_rush:
        rush_pkgs_in_this_zip = [x for x in config.hub_package_list if config.all_packages_by_id[x].zip == z and x in rush_ready_at_800am_ids]

        if not rush_pkgs_in_this_zip:
            continue

        # sort packages in `rush_pkgs_in_this_zip` by address so that packages to same address are delivered at same time
        rush_tuple = [(x, config.all_packages_by_id[x].street_address) for x in rush_pkgs_in_this_zip]
        rush_tuple.sort(key=lambda x:x[1])
        rush_pkgs_in_this_zip = [x[0] for x in rush_tuple]
        for p in rush_pkgs_in_this_zip:
            truck1.add_package(p)
    
    # now add nonrush packages from west to east for zips that the truck already has packages for
    for z in config.zips_from_west_to_east_nonrush:
        for p in config.hub_package_list:
            if len(truck1.bill_of_lading) == 16:
                break
            if z in truck1.delivery_zips and config.all_packages_by_id[p].zip == z:
                truck1.add_package(p)
    
    truck1.end_run()

    truck2 = Truck('truck 2') # truck 2's first run leaves at 9:05 am
    # special features of this run:
    #  - rush packages (morning deadline): #6, #25
    #  - delayed packages: #6, #25, #28, #32
    #  - packages with vehicle affinities: #3, #18, #36, #38
    truck2.start_time_this_run = '9:05 am'
    # load delayed packages
    delayed_packages = [x for x in config.hub_package_list if config.all_packages_by_id[x].when_can_leave_hub > my_time.convert_time_to_minutes_offset('8:00 am') and config.all_packages_by_id[x].when_can_leave_hub <= my_time.convert_time_to_minutes_offset('9:05 am')]
    for p in delayed_packages:
        truck2.add_package(p)
    # load packages with affinity to truck 2
    affinity_packages = [x for x in config.hub_package_list if config.all_packages_by_id[x].truck_affinity == 'truck 2']
    # print(affinity_packages)
    for p in affinity_packages:
        truck2.add_package(p)
    # now add more packages from west to east for zips that the truck already has packages for
    for z in config.zips_from_west_to_east_nonrush:
        for p in config.hub_package_list:
            if len(truck2.bill_of_lading) == 16:
                break
            if config.all_packages_by_id[p].zip == z:
                truck2.add_package(p)
    truck2.end_run()
    
    # truck 1's second run leaves at 10:20 am
    # special features of this run:
    #  - delayed packages: #9
    # truck1.start_time_this_run = '11:00 am'
    for z in config.zips_from_west_to_east_nonrush:
        this_zip = []
        for p in config.hub_package_list:
            if len(truck1.bill_of_lading) == 16:
                break
            if config.all_packages_by_id[p].zip == z:
                this_zip.append(p)
        for x in this_zip:
            truck1.add_package(x)
    truck1.end_run()

    print(config.hub_stats_miles)
    print(config.hub_package_list)



    


    

    
    



        





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