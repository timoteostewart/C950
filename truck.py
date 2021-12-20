class Truck:
    def __init__(self, truck_name) -> None:
        self.truck_name: str = truck_name
        self.truck_number: int = int(truck_name[-1])
        
        self.mileage_for_this_run_so_far = 0.0
        self.mileage_for_earlier_runs: float = 0.0
        
        self.cur_num_pkgs: int = 0
        self.num_pkgs_being_delivered_now: int = 0
        
        self.base_status: str = '' # 'at hub', 'departing hub', 'en route', 'delivering', 'returning'
        self.detailed_status: str = ''
        self.cur_stop_street_address: str = ''
