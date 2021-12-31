from dataclasses import dataclass


@dataclass
class Truck:
    def __init__(self, truck_name) -> None:
        self.truck_name: str = truck_name
        self.truck_number: int = int(truck_name[-1])
        
        self.mileage_for_this_route_so_far: float = 0.0
        self.cumulative_mileage_for_the_day: float = 0.0
        self.cumulative_mileage_for_the_day_display: float = 0.0
        
        self.cur_num_pkgs: int = 0
        self.num_pkgs_being_delivered_now: int = 0
        
        self.base_status: str = ''  # possible values: 'at hub', 'departing hub', 'en route', 'delivering', 'returning', 'back at hub'
        self.detailed_status: str = ''
        self.cur_stop_street_address: str = ''
        self.list_of_packages_delivered_to_this_stop = []
