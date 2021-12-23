import copy
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

        album = Album()

        trucks = [None, Truck('truck 1'), Truck('truck 2')] # skip zeroth element so that truck numbers are indexes
        # load initial truck statuses
        trucks[1].base_status = 'at hub'
        trucks[2].base_status = 'at hub'

        sevenfiftynine = Snapshot(-1)
        # load initial package statuses that were set during package ingestion
        for p_id in range(1, 41):
            sevenfiftynine.package_statuses[p_id] = config.all_packages_by_id_ht.get(p_id).delivery_status
        sevenfiftynine.is_key_frame = True
        album.check_in_snapshot(sevenfiftynine, copy.copy(trucks[1]))
        album.check_in_snapshot(sevenfiftynine, copy.copy(trucks[2]))

        for route in self.route_list.routes:

            snapshot_for_minute_of_departure = Snapshot(route.departure_time_as_offset)
            
            if route.return_time_as_offset > album.final_return_to_hub_as_offset:
                album.final_return_to_hub_as_offset = route.return_time_as_offset # `album.final_return_to_hub_as_offset` will tell us how many snapshots we need

            cur_time_as_offset = route.departure_time_as_offset
            cur_truck = trucks[route.truck_number]
            cur_truck.base_status = 'departing hub'
            cur_truck.cur_num_pkgs = len(route.package_manifest)
            cur_truck.cur_stop_street_address = geo.HUB_STREET_ADDRESS
            
            cur_truck.mileage_for_this_route_so_far = 0.0
            
            on_truck_status = f"aboard truck {cur_truck.truck_number}"
            for pkg in route.package_manifest:
                pkg.delivery_status = on_truck_status
                snapshot_for_minute_of_departure.package_statuses[pkg.id] = on_truck_status
            
            snapshot_for_minute_of_departure.is_key_frame = True
            album.check_in_snapshot(snapshot_for_minute_of_departure, copy.copy(cur_truck))

            for i, _ in enumerate(route.ordered_list_of_stops):
                
                if i == 0:
                    continue # skip hub stop, since it was in `snapshot_for_minute_of_departure``
                
                prev_stop = route.ordered_list_of_stops[i-1]
                cur_stop = route.ordered_list_of_stops[i]
                cur_truck.cur_stop_street_address = cur_stop.street_address

                leg_distance = config.distances_between_pairs_ht.get(f"{prev_stop.street_address} and {cur_stop.street_address}")
                cur_truck.mileage_for_this_route_so_far += leg_distance
                cur_truck.cumulative_mileage_for_the_day_display += leg_distance
                
                leg_time = int(math.ceil(leg_distance * config.MINUTES_PER_MILE)) # round time up to next minute
                cur_time_as_offset += leg_time

                cur_snapshot = Snapshot(cur_time_as_offset)
                
                cur_truck.num_pkgs_being_delivered_now = 0
                cur_truck.list_of_packages_delivered_to_this_stop = []
                for pkg in route.package_manifest:
                    delivered_status = f"dlvrd @{my_time.convert_minutes_offset_to_time(cur_time_as_offset)}"
                    if pkg.street_address == cur_stop.street_address:
                        cur_truck.list_of_packages_delivered_to_this_stop.append(pkg.id)
                        cur_truck.num_pkgs_being_delivered_now += 1
                        cur_truck.cur_num_pkgs -= 1
                        cur_snapshot.package_statuses[pkg.id] = delivered_status

                if cur_stop == geo.HUB_STOP:
                    cur_truck.base_status = 'back at hub'
                    cur_truck.mileage_for_this_route_so_far = route.distance_traveled_in_miles
                    cur_truck.cumulative_mileage_for_the_day += route.distance_traveled_in_miles
                    cur_truck.cumulative_mileage_for_the_day_display = cur_truck.cumulative_mileage_for_the_day
                else:
                    if cur_truck.cur_num_pkgs == 0 and cur_truck.num_pkgs_being_delivered_now > 0:
                        cur_truck.base_status = 'last stop'
                    else:
                        cur_truck.base_status = 'delivering'

                cur_snapshot.is_key_frame = True
                album.check_in_snapshot(cur_snapshot, cur_truck)

        
        for route in self.route_list.routes:
            self.route_list.truck_mileage_for_the_day[route.truck_number] += route.distance_traveled_in_miles
        
        album.snapshots[album.final_return_to_hub_as_offset].all_trucks_cumulative_mileage_for_day = self.route_list.truck_mileage_for_the_day[1] + self.route_list.truck_mileage_for_the_day[2]

        album.snapshots[album.final_return_to_hub_as_offset].all_trucks_cumulative_mileage_for_day = self.route_list.truck_mileage_for_the_day[1] + self.route_list.truck_mileage_for_the_day[2]
        album.interpolate_snapshots()

        return album


