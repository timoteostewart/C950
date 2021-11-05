# {student_name: "Tim Stewart", student_id: "001476583"}

from custodian import Custodian
from operator import attrgetter
from package import Package
from collections import defaultdict

from hash_table import HashTable
from truck import Truck

import location
import data

if __name__ == '__main__':

    # entities that can have custody of packages
    hub_package_list = []
    delivered_list = []
    
    
    # TODO: ingest distances
    zips_from_west_to_east = [84118, 84123, 84119, 84104, 84103, 84111, 84115, 84117, 84106, 84105, 84121]
    all_packages_by_zip = defaultdict(list) # 12 distinct delivery codes
    for z in zips_from_west_to_east:
        all_packages_by_zip[str(z)] = []
    
    all_packages_by_id_ht = HashTable(60)
    
    disjoint_set = [0] * 41 # indices correlates to package IDs
    data.ingest_packages(all_packages_by_id_ht, all_packages_by_zip, hub_package_list)


    # 8:00 am
    current_time = 0
    
    # load packages that have morning deadline
    rush_set_ids = set()
    nonrush_set_ids = set()

    # populate `rush_set_ids` with packages with morning deadlines and packages they have to be delivered with
    for p_id in hub_package_list:
        p = all_packages_by_id_ht.get_or_default(str(p_id), '')
        if p.deadline < 1440 and p.when_can_leave_hub <= current_time:
            rush_set_ids.add(p_id)

            if p.package_affinities != {0}:
                for each_affinity_id in p.package_affinities:
                    rush_set_ids.add(each_affinity_id)
    
    # populate `nonrush_set_ids` with all other packages
    for p_id in hub_package_list:
        if p_id not in rush_set_ids:
            nonrush_set_ids.add(p_id)

    # print(all_packages_by_zip)
    # print(rush_set_ids)

    west_truck = Truck('truck 1')
    east_truck = Truck('truck 2')

    # load rush packages
    # load west truck first, then east truck
    target_truck = west_truck
    for zip in zips_from_west_to_east:
        rush_packages_in_cur_zip = list(set(all_packages_by_zip[str(zip)]).intersection(rush_set_ids))

        if rush_packages_in_cur_zip == []:
            continue
        
        # switch to east truck when west truck has half the rush packages
        if len(west_truck.bill_of_lading) >= len(rush_set_ids) // 2:
            target_truck = east_truck

        target_truck.delivery_zips.append(zip)
        for x in rush_packages_in_cur_zip:
            target_truck.bill_of_lading.append(x)

    # print(west_truck.bill_of_lading)
    # print(west_truck.delivery_zips)
    # print(east_truck.bill_of_lading)
    # print(east_truck.delivery_zips)

    # load nonrush packages, observing any truck affinity restrictions
    # TODO
    
    for x in nonrush_set_ids:
        

    

    
    



        





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