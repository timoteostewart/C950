# {student_name: "Tim Stewart", student_id: "001476583"}

from functools import reduce
from operator import attrgetter, index
from os import closerange

import config
import data
import geo
import my_package
import my_time
import route
import truck

if __name__ == '__main__':

    data.ingest_distances()
    data.ingest_packages()


    eight_oclock_route_1 = route.Route()
    eight_oclock_route_2 = route.Route()
    eight_oclock_route_1, eight_oclock_route_2 = route.populate_two_routes_for_the_given_time('8:00 am')

    print(sorted([x.id for x in eight_oclock_route_1.manifest_required_packages]))
    print(sorted([x.id for x in eight_oclock_route_1.manifest_optional_packages]))
    print(my_time.convert_minutes_offset_to_time(config.MINUTES_PER_MILE * geo.distance_of_path_of_stops(eight_oclock_route_1.circuit)))
    
    print(eight_oclock_route_2)
    print(my_time.convert_minutes_offset_to_time(config.MINUTES_PER_MILE * geo.distance_of_path_of_stops(eight_oclock_route_2.circuit)))

    # print(eight_oclock_route_2)
    # print(len(eight_oclock_route_2.manifest_all_packages))
    # print(my_time.convert_minutes_offset_to_time(config.MINUTES_PER_MILE * geo.distance_of_path_of_stops(eight_oclock_route_2.circuit)))
    # print(len(config.packages_at_hub))
    
    # print([x.id for x in eight_oclock_route_1.manifest_all_packages])
    # print([x.id for x in eight_oclock_route_2.manifest_all_packages])

    nineohfive_route_1 = route.Route()
    nineohfive_route_2 = route.Route()
    nineohfive_route_1, nineohfive_route_2 = route.populate_two_routes_for_the_given_time('9:05 am')

    # print(len(nineohfive_route_1.manifest_all_packages))
    # print(len(nineohfive_route_2.manifest_all_packages))

    # print(len(config.packages_at_hub))


    
    
    # add additional packages
    # TODO: if we still have room on the truck, then geographically proximate stops could be added to circuit

    # print(len(eight_oclock_route_1.manifest_all_packages))
    # print(len(eight_oclock_route_1.manifest_optional_packages))



    exit()


    # TODO: if a delivery is late, try reversing the circuit and see if that fixes it



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