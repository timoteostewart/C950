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


    first_route, pkgs_remaining = route.populate_one_route('8:00 am', config.packages_at_hub)
    print(route.validate_route(first_route, '8:00 am', reverse=True))

    # second_route, pkgs_remaining = route.populate_one_route_for_a_given_time('8:01 am', pkgs_remaining)
    # print(route.validate_route(second_route, '8:01 am', reverse=True))

    third_route, pkgs_remaining = route.populate_one_route('9:05 am', pkgs_remaining)
    print(route.validate_route(third_route, '9:05 am', reverse=True))

    fourth_route, pkgs_remaining = route.populate_one_route('10:20 am', pkgs_remaining)
    print(route.validate_route(fourth_route, '10:20 am', reverse=True))

    print(sorted([pkg.id for pkg in pkgs_remaining]))
    print(config.cumulative_miles)
    exit()

    