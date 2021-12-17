import my_time

def truncate_float_to_tenths_place_for_display(f: float):
    f_as_string = str(f)
    index_of_decimal = f_as_string.find('.')
    return f_as_string[slice(0, index_of_decimal + 2)]

def right_pad_to_15_chars(s: str):
    if not s:
        return '               '

    s = str(s)

    if len(s) > 15:
        return s.slice(0, 15)
    else:
        while len(s) < 15:
            s += ' '
        return s


class Snapshot:
    def __init__(self) -> None:
        self.current_time_as_offset: int = -1
        self.current_time_as_display: str = ''

        # truck 1
        self.truck_1_mileage_for_this_run_so_far: float = 0.0
        self.truck_1_mileage_for_earlier_runs: float = 0.0
        self.truck_1_cur_num_pkgs: int = -1
        self.truck_1_num_pkgs_being_delivered_now: int = -1
        self.truck_1_base_status: str = '' # 'at hub', 'departing hub', 'en route', 'delivering', 'returning'
        self.truck_1_detailed_status: str = ''
        self.truck_1_cur_stop_street_address: str = ''

        # truck 2
        self.truck_2_mileage_for_this_run_so_far: float = 0.0
        self.truck_2_mileage_for_earlier_runs: float = 0.0
        self.truck_2_cur_num_pkgs: int = -1
        self.truck_2_num_pkgs_being_delivered_now: int = -1
        self.truck_2_base_status: str = '' # 'at hub', 'departing hub', 'en route', 'delivering', 'returning'
        self.truck_2_detailed_status: str = ''
        self.truck_2_cur_stop_street_address: str = ''

        # packages
        self.package_statuses = [None] * 41 # array with package id as index

        # computed values
        self.truck_1_cumulative_mileage_for_the_day: float = 0.0
        self.all_trucks_cumulative_mileage_for_the_day: float = 0.0
        

    def update_computed_values(self, package_manifest):
        # time
        self.current_time_as_display = my_time.convert_minutes_offset_to_time(self.current_time_as_offset)
        if len(self.current_time_as_display) == 7:
            self.current_time_as_display = self.current_time_as_display  + ' ' # pad right

        # cumulative data
        # TODO: for display, truncate all mileages after tenths place
        # TODO: for all trucks mileage, be sure to pad right correctly
        self.truck_1_cumulative_mileage_for_the_day = self.truck_1_mileage_for_this_run_so_far + self.truck_1_mileage_for_earlier_runs
        self.truck_2_cumulative_mileage_for_the_day = self.truck_2_mileage_for_this_run_so_far + self.truck_2_mileage_for_earlier_runs
        self.all_trucks_cumulative_mileage_for_the_day = self.truck_1_cumulative_mileage_for_the_day + self.truck_2_cumulative_mileage_for_the_day
        
        # trucks
        if self.truck_1_base_status == 'at hub':
            self.truck_1_detailed_status = f"at hub (traveled {self.truck_1_cumulative_mileage_for_the_day} miles so far today)"
        elif self.truck_1_base_status == 'departing hub':
            self.truck_1_detailed_status = f"departing hub with {self.truck_1_cur_num_pkgs} packages"
        elif self.truck_1_base_status == 'en route':
            self.truck_1_detailed_status = f"en route with {self.truck_1_cur_num_pkgs} packages ({self.truck_1_mileage_for_this_run_so_far} miles traveled since hub)"
        elif self.truck_1_base_status == 'delivering':
            self.truck_1_detailed_status = f"delivering {self.truck_1_num_pkgs_being_delivered_now} packages to {self.truck_1_cur_stop_street_address}"
        elif self.truck_1_base_status == 'returning':
            self.truck_1_detailed_status = f"returning to hub empty ({self.truck_1_mileage_for_this_run_so_far} miles traveled since hub)"
        
        # packages
        for pkg in package_manifest:
            if pkg.delivery_status == 'being dlvrd now':
                pkg.delivery_status = f"dlvrd @{my_time.convert_minutes_offset_to_time(self.current_time_as_offset - 1)}"
            self.package_statuses[pkg.id] = pkg.delivery_status
            

    def display(self):

        # construct truck status lines
        # TODO

        # construct package status lines
        all_package_statuses = ''
        for row_num in range(1, 11):
            if row_num == 10:
                cur_row = ''
            else:
                cur_row = ' '
            for pkg_ids_this_row in range(0, 31, 10):
                cur_row += f"{str(row_num + pkg_ids_this_row)} {right_pad_to_15_chars(self.package_statuses[row_num + pkg_ids_this_row])}  "
            all_package_statuses += cur_row
            all_package_statuses += '\n'

        print(f""
        f"Delivery Log Inspector for WGU package delivery system\n"
        f"Current time: 00:00 am    Commands: 't': go to time,  'p' play,  'q': quit\n"
        f"All trucks mileage so far: 000.0    'a': ← 1 hr,  's': ← 10 min,  'd': ← 1 min\n"
        f"T# Status                           'j': → 1 min,  'k': → 10 min,  'l': → 1 hr\n"
        f"-- ---------------------------------------------------------------------------\n"
        f"1 at hub (traveled 42.1 miles so far today)\n"
        f"1 departing hub with 16 packages\n"
        f"1 en route with 15 packages (traveled 0.0 miles since hub)\n"
        f"2 en route with 2 packages\n"
        f"1 delivering 2 pkgs at 3575 W Valley Central Station Bus Loop\n"
        f"2 returning to hub empty (traveled 0.0 miles since hub)\n"
        f" \n"
        f"P# Status           P# Status           P# Status           P# Status         \n"
        f"-- ---------------  -- ---------------  -- ---------------  -- ---------------\n"
        f"{all_package_statuses}"
        f"")
        