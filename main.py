# {student_name: "Tim Stewart", student_id: "001476583"}

from operator import attrgetter

from package import Package
from truck import Truck

import config
import location
import data

if __name__ == '__main__':

    
    data.ingest_distances()

    config.distances_between_pairs.dump()

    exit()
    
    
    for z in config.zips_from_west_to_east:
        config.all_packages_by_zip[str(z)] = []
    
    data.ingest_packages()

    current_time = 0 # 8:00 am
    
    # load packages that have morning deadline
    rush_set_ids = set()
    nonrush_set_ids = set()

    # populate `rush_set_ids` with packages with morning deadlines _and_ with packages they have to be delivered with
    for p_id in config.hub_package_list:
        p = config.all_packages_by_id_ht.get_or_default(str(p_id), '')
        if p.deadline < 1440 and p.when_can_leave_hub <= current_time:
            rush_set_ids.add(p_id)

            if p.package_affinities != {0}:
                for each_affinity_id in p.package_affinities:
                    rush_set_ids.add(each_affinity_id)
    
    # populate `nonrush_set_ids` with all other packages
    for p_id in config.hub_package_list:
        if p_id not in rush_set_ids:
            nonrush_set_ids.add(p_id)

    
    






    

    
    



        





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