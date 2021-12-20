import copy

import config
import geo
import math
import my_time

import album

from my_package import Package
from truck import Truck


def truncate_float_to_tenths_place_for_display(f: float):
    f_as_string = str(f)
    index_of_decimal = f_as_string.find('.')
    return f_as_string[slice(0, index_of_decimal + 2)]


def right_pad_to_15_chars(s: str):
    if not s:
        return '               '

    s = str(s)

    if len(s) > 15:
        return s[slice(0, 15)]
    else:
        while len(s) < 15:
            s += ' '
        return s


def bold_text(s: str):
    return '\u001b[37;1m' + s + '\u001b[0m'


class Snapshot:
    def __init__(self, current_time_as_offset) -> None:
        self.current_time_as_offset: int = current_time_as_offset
        self.current_time_as_display: str = ''

        self.trucks = []
        self.trucks.append(None) # skip zeroth element so that indexes match truck numbers
        self.trucks.append(Truck('truck 1')) # trucks[1]
        self.trucks.append(Truck('truck 2')) # trucks[2]

        # packages
        self.package_statuses = [None] * 41 # array with package id as index

        # computed values
        self.truck_1_cumulative_mileage_for_the_day: float = -1.0
        self.all_trucks_cumulative_mileage_for_the_day: float = -1.0
        

    def update_computed_values(self):
        # time
        self.current_time_as_display = my_time.convert_minutes_offset_to_time(self.current_time_as_offset)
        if len(self.current_time_as_display) == 7:
            self.current_time_as_display = self.current_time_as_display  + ' ' # pad right

        # cumulative data
        # TODO: for display, truncate all mileages after tenths place
        # TODO: for all trucks mileage, be sure to pad right correctly
        # trucks
        for truck_num in [1, 2]:
            self.trucks[truck_num].cumulative_mileage_for_the_day = self.trucks[truck_num].mileage_for_this_run_so_far + self.trucks[truck_num].mileage_for_earlier_runs
            self.trucks[truck_num].cumulative_mileage_for_the_day = self.trucks[truck_num].mileage_for_this_run_so_far + self.trucks[truck_num].mileage_for_earlier_runs
            if self.trucks[truck_num].base_status == 'at hub':
                self.trucks[truck_num].detailed_status = f"at hub (traveled {self.trucks[truck_num].cumulative_mileage_for_the_day} miles so far today)"
            elif self.trucks[truck_num].base_status == 'back at hub':
                self.trucks[truck_num].detailed_status = f"back at hub"
            elif self.trucks[truck_num].base_status == 'departing hub':
                self.trucks[truck_num].detailed_status = f"departing hub with {self.trucks[truck_num].cur_num_pkgs} {'package' if self.trucks[truck_num].cur_num_pkgs == 1 else 'packages'}"
            elif self.trucks[truck_num].base_status == 'en route':
                self.trucks[truck_num].detailed_status = f"en route with {self.trucks[truck_num].cur_num_pkgs} {'package' if self.trucks[truck_num].cur_num_pkgs == 1 else 'packages'} ({self.trucks[truck_num].mileage_for_this_run_so_far} miles traveled since hub)"
            elif self.trucks[truck_num].base_status == 'delivering':
                self.trucks[truck_num].detailed_status = f"delivering {self.trucks[truck_num].num_pkgs_being_delivered_now} {'package' if self.trucks[truck_num].num_pkgs_being_delivered_now == 1 else 'packages'} to {self.trucks[truck_num].cur_stop_street_address}"
            elif self.trucks[truck_num].base_status == 'returning':
                self.trucks[truck_num].detailed_status = f"returning to hub empty ({self.trucks[truck_num].mileage_for_this_run_so_far} miles traveled since hub)"
        
        self.all_trucks_cumulative_mileage_for_the_day = self.trucks[1].cumulative_mileage_for_the_day + self.trucks[2].cumulative_mileage_for_the_day

        # packages

    

    def update_package_status_for_pkgs_this_run(self, package_manifest: list[Package]):
        for pkg in package_manifest:
            self.package_statuses[pkg.id] = 'on truck'


    def load_truck_details(self, truck: Truck):
        self.trucks[truck.truck_number] = copy.copy(truck)


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

        print(f"\n"
        f"==============================================================================\n"
        f"Delivery Log Inspector for WGU package delivery system\n"
        f"Current time: {bold_text(self.current_time_as_display)}    Commands: 't': go to time,  'p' play,  'q': quit\n"
        f"All trucks mileage so far: 000.0    'a': ← 1 hr,  's': ← 10 min,  'd': ← 1 min\n"
        f"T# Status                           'j': → 1 min,  'k': → 10 min,  'l': → 1 hr\n"
        f"-- ---------------------------------------------------------------------------\n"
        f"1 {self.trucks[1].detailed_status}\n"
        f"2 {self.trucks[2].detailed_status}\n"
        # f"1 at hub (traveled 42.1 miles so far today)\n"
        # f"1 departing hub with 16 packages\n"
        # f"1 en route with 15 packages (traveled 0.0 miles since hub)\n"
        # f"2 en route with 2 packages\n"
        # f"1 delivering 2 pkgs at 3575 W Valley Central Station Bus Loop\n"
        # f"2 returning to hub empty (traveled 0.0 miles since hub)\n"
        f" \n"
        f"P# Status           P# Status           P# Status           P# Status         \n"
        f"-- ---------------  -- ---------------  -- ---------------  -- ---------------\n"
        f"{all_package_statuses}"
        f"")
        
