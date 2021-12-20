import math

import album
import config
import geo
import my_time
import snapshot
import truck

from album import Album
from route import RouteList
from snapshot import Snapshot
from truck import Truck

class DeliveryScheduleWriter:
    
    def __init__(self, route_list: RouteList) -> None:
        self.route_list = route_list


    def populate_album_with_snapshots(self) -> Album:

        if not self.route_list:
            print("Thisself.route_list is empty!")
            return

        album = Album()
        
        sevenfiftynine = Snapshot(-1)
        # load initial package statuses that were set during package ingestion
        for p_id in range(1, 41):
            sevenfiftynine.package_statuses[p_id] = config.all_packages_by_id_ht.get(p_id).delivery_status
        # load initial truck statuses
        sevenfiftynine.trucks[1].base_status = 'at hub'
        sevenfiftynine.trucks[2].base_status = 'at hub'
        # sevenfiftynine.display()
        album.merge_snapshot(sevenfiftynine, sevenfiftynine.trucks[1])
        album.merge_snapshot(sevenfiftynine, sevenfiftynine.trucks[2])

        for route in self.route_list.routes:

            s = Snapshot(route.departure_time_as_offset)
            
            if route.return_time_as_offset > album.final_return_to_hub_as_offset:
                album.final_return_to_hub_as_offset = route.return_time_as_offset # `album.final_return_to_hub_as_offset` will tell us how many snapshots we need

            cur_time = route.departure_time_as_offset

            cur_truck = Truck(route.truck_name)
            cur_truck.base_status = 'departing hub'
            cur_truck.cur_num_pkgs = len(route.package_manifest)
            cur_truck.cur_stop_street_address = geo.HUB_STREET_ADDRESS
            on_truck_status = f"on {cur_truck.truck_name}"
            for pkg in route.package_manifest:
                pkg.delivery_status = on_truck_status
            s.load_truck_details(cur_truck)

            for pkg in route.package_manifest:
                s.package_statuses[pkg.id] = 'loaded on T #{cur_truck.truck_number}'
            
            album.merge_snapshot(s, cur_truck)

            for i, _ in enumerate(route.ordered_list_of_stops):
                if i == 0:
                    continue # skip first element in ordered list of stops, which is just the hub
                
                prev_stop = route.ordered_list_of_stops[i-1]
                cur_stop = route.ordered_list_of_stops[i]
                leg_distance = config.distances_between_pairs_ht.get(f"{prev_stop.street_address} and {cur_stop.street_address}")
                
                if cur_stop.street_address == geo.HUB_STREET_ADDRESS:
                    cur_truck.base_status = 'back at hub'
                else:
                    cur_truck.base_status = 'delivering'
                
                cur_truck.cur_stop_street_address = cur_stop.street_address
                cur_truck.mileage_for_this_run_so_far += leg_distance
                
                leg_time = int(math.ceil(leg_distance * config.MINUTES_PER_MILE)) # round time up to next minute
                cur_time += leg_time

                s2 = Snapshot(cur_time)
                
                cur_truck.num_pkgs_being_delivered_now = 0
                for pkg in route.package_manifest:
                    delivered_status = f"dlvrd @{my_time.convert_minutes_offset_to_time(cur_time)}"
                    if pkg.street_address == cur_stop.street_address:
                        cur_truck.num_pkgs_being_delivered_now += 1
                        cur_truck.cur_num_pkgs -= 1
                        s2.package_statuses[pkg.id] = delivered_status

                        # if pkg.deadline_as_offset == 1440:
                        #     print(f"{route.truck_name} delivered nonrush package {pkg.id} at {my_time.convert_minutes_offset_to_time(cur_time)}", end='')
                    # else:
                    #     print(f"{route.truck_name} delivered    rush package {pkg.id} at {my_time.convert_minutes_offset_to_time(cur_time)} (deadline is {my_time.convert_minutes_offset_to_time(pkg.deadline_as_offset)})", end='')
                    # if pkg.truck_affinity:
                    #     print(f"                        (affinity {pkg.truck_affinity})")
                    # else:
                    #     print("")

            
                album.merge_snapshot(s2, cur_truck)

        return album


