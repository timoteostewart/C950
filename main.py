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

    # 8:00 am
    eight_oclock_route_1 = route.Route('8am1')
    eight_oclock_route_2 = route.Route('8am2')
    eight_oclock_route_1, eight_oclock_route_2 = route.populate_two_routes_for_the_given_time('8:00 am')

    # eight_oclock_route_1only = route.Route('8am1only')

    # print("route 1only")
    print(f"required: {sorted([x.id for x in eight_oclock_route_1.manifest_required_packages])}")
    print(f"optional: {sorted([x.id for x in eight_oclock_route_1.manifest_optional_packages])}")
    # print(my_time.convert_minutes_offset_to_time(config.MINUTES_PER_MILE * geo.distance_of_path_of_stops(eight_oclock_route_1.circuit)))
    print(route.validate_route(eight_oclock_route_1, '8:00 am', reverse=True))
    
    # print("route 2")
    # print(f"required: {sorted([x.id for x in eight_oclock_route_2.manifest_required_packages])}")
    # print(f"optional: {sorted([x.id for x in eight_oclock_route_2.manifest_optional_packages])}")
    # print(my_time.convert_minutes_offset_to_time(config.MINUTES_PER_MILE * geo.distance_of_path_of_stops(eight_oclock_route_2.circuit)))

    eight_oclock_route_1.convert_circuit_to_package_delivery_order()

    exit()

    # 10:20 am
    ten_twenty_route_1 = route.Route()
    ten_twenty_route_2 = route.Route()
    ten_twenty_route_1, ten_twenty_route_2 = route.populate_two_routes_for_the_given_time('10:20 am')

    print("route 1")
    print(f"required: {sorted([x.id for x in ten_twenty_route_1.manifest_required_packages])}")
    print(f"optional: {sorted([x.id for x in ten_twenty_route_1.manifest_optional_packages])}")
    print(my_time.convert_minutes_offset_to_time(140 + config.MINUTES_PER_MILE * geo.distance_of_path_of_stops(ten_twenty_route_1.circuit)))
    
    print("route 2")
    print(f"required: {sorted([x.id for x in ten_twenty_route_2.manifest_required_packages])}")
    print(f"optional: {sorted([x.id for x in ten_twenty_route_2.manifest_optional_packages])}")
    print(my_time.convert_minutes_offset_to_time(140 + config.MINUTES_PER_MILE * geo.distance_of_path_of_stops(ten_twenty_route_2.circuit)))



    
    # add additional packages
    # TODO: if we still have room on the truck, then geographically proximate stops could be added to circuit

    # print(len(eight_oclock_route_1.manifest_all_packages))
    # print(len(eight_oclock_route_1.manifest_optional_packages))



    exit()

    