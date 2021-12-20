import snapshot
import truck

class Album:
    def __init__(self) -> None:
        self.snapshots: list[snapshot.Snapshot] = [None] * (8 * 60) # up to 8 hours of delivery data, granular to 1-minute increments, so we'll store up to 8 * 60 (== 480) snapshots of package statuses and truck mileage stats
        # note that snapshots[-1] will store the snapshot for 7:59 am
        self.final_return_to_hub_as_offset = -1

    def interpolate_snapshots(self):
        # TODO: if previous snapshot has 'delivering now' for a snapshot,
        #       then update it to 'dlvrd @00:00 am'
        pass

    def merge_snapshot(self, incoming_snapshot: snapshot.Snapshot, t: truck.Truck):
        incoming_snapshot.load_truck_details(t)
        incoming_snapshot.update_computed_values()

        existing_snapshot = self.snapshots[incoming_snapshot.current_time_as_offset]
        
        if not existing_snapshot:
            self.snapshots[incoming_snapshot.current_time_as_offset] = incoming_snapshot
        else:
            pass
            # TODO: merge snapshots
            # merge package statuses
            for p_id in range(1, 41):
                current_status = existing_snapshot.package_statuses[p_id]
                incoming_status = incoming_snapshot.package_statuses[p_id]
                if current_status == None:
                    existing_snapshot.package_statuses[p_id] = incoming_status
                elif incoming_status == None:
                    pass # no action necessary

            
            # TODO: merge truck info
            
            

    
    def display_active_snapshots(self):
        self.snapshots[-1].display()
        for s in self.snapshots:
            if s and s.current_time_as_offset != -1:
                s.display()
            