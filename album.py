import copy

import config
import snapshot
import truck

from snapshot import Snapshot
from truck import Truck

def update_truck_mileage_during_interpolation(truck: Truck):
    if not (truck.base_status == 'at hub' or truck.base_status == 'back at hub'):
        truck.mileage_for_this_route_so_far += config.MILES_PER_MINUTE
        truck.cumulative_mileage_for_the_day += config.MILES_PER_MINUTE


class Album:
    def __init__(self) -> None:
        self.snapshots: list[snapshot.Snapshot] = [None] * (8 * 60) # up to 8 hours of delivery data, granular to 1-minute increments, so we'll store up to 8 * 60 (== 480) snapshots of package statuses and truck mileage stats
        # note that snapshots[-1] will store the snapshot for 7:59 am
        self.final_return_to_hub_as_offset = -1


    def interpolate_snapshots(self):
        for cur_offset in range(0, self.final_return_to_hub_as_offset + 1):

            cur_snapshot = self.snapshots[cur_offset]
            prev_snapshot = self.snapshots[cur_offset-1]
            
            # if no snapshot yet for this minute, create it
            if not cur_snapshot:
                self.snapshots[cur_offset] = Snapshot(cur_offset)
                cur_snapshot = self.snapshots[cur_offset]

            # carry forward package info
            for p_id in range(1, 41):
                if cur_snapshot.package_statuses[p_id] == None:
                    cur_snapshot.package_statuses[p_id] = prev_snapshot.package_statuses[p_id]

            # carry forward truck info
            # case 1: neither truck took action in this minute
            if not cur_snapshot.trucks[1] and not cur_snapshot.trucks[2]:
                for truck_num in [1, 2]:
                    cur_snapshot.trucks[truck_num] = copy.copy(prev_snapshot.trucks[truck_num])
                    update_truck_mileage_during_interpolation(cur_snapshot.trucks[truck_num])
            
            # case 2: one truck took action in this minute
            elif (cur_snapshot.trucks[1] and not cur_snapshot.trucks[2]) or (cur_snapshot.trucks[2] and not cur_snapshot.trucks[1]):
                inactive_truck_num = 2 if cur_snapshot.trucks[1] else 1
                cur_snapshot.trucks[inactive_truck_num] = copy.copy(prev_snapshot.trucks[inactive_truck_num])
                update_truck_mileage_during_interpolation(cur_snapshot.trucks[inactive_truck_num])

            # case 3: both trucks took action in this minute
            else: # cur_snapshot.trucks[1] and cur_snapshot.trucks[2]:
                pass # preserve the trucks' existing details
                
            # all cases: update truck statuses as needed
            for truck_num in [1, 2]:
                if prev_snapshot.trucks[truck_num].base_status == 'departing hub' or prev_snapshot.trucks[truck_num].base_status == 'delivering':
                    cur_snapshot.trucks[truck_num].base_status = 'en route'
                elif prev_snapshot.trucks[truck_num].base_status == 'back at hub':
                    cur_snapshot.trucks[truck_num].base_status = 'at hub'
                elif prev_snapshot.trucks[truck_num].base_status == 'last stop':
                    cur_snapshot.trucks[truck_num].base_status = 'returning'

            # update `self.all_trucks_cumulative_mileage_for_day`
            if cur_snapshot.all_trucks_cumulative_mileage_for_day == -1.0:
                cur_snapshot.all_trucks_cumulative_mileage_for_day = cur_snapshot.trucks[1].cumulative_mileage_for_the_day + cur_snapshot.trucks[2].cumulative_mileage_for_the_day

            # update truck statuses
            cur_snapshot.expand_truck_base_statuses_to_detailed_statuses()
        

    def check_in_snapshot(self, incoming_snapshot: snapshot.Snapshot, truck: truck.Truck):
        truck.list_of_packages_delivered_to_this_stop.sort()
        incoming_snapshot.trucks[truck.truck_number] = truck

        cur_snapshot = self.snapshots[incoming_snapshot.current_time_as_offset]

        # case 1: no snapshot yet (since other truck hasn't taken action in this minute yet),
        #       so create a snapshot
        if not cur_snapshot:
            incoming_snapshot.trucks[truck.truck_number] = truck
            incoming_snapshot.expand_truck_base_statuses_to_detailed_statuses()
            self.snapshots[incoming_snapshot.current_time_as_offset] = incoming_snapshot
            return
        
        # case 2: a snapshot exists (since other truck already took action in this minute),
        #       so merge snapshots
        
        # first, merge incoming package statuses
        for p_id in range(1, 41):
            incoming_status = incoming_snapshot.package_statuses[p_id]
            if incoming_status != None:
                cur_snapshot.package_statuses[p_id] = incoming_status

        # then, copy incoming truck into current snapshot
        cur_snapshot.trucks[truck.truck_number] = copy.copy(truck)
        cur_snapshot.expand_truck_base_statuses_to_detailed_statuses()

    
    def display_active_snapshots(self):
        self.snapshots[-1].display()
        for s in self.snapshots:
            if s and s.current_time_as_offset != -1:
                s.display()
            