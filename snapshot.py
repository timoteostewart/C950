import copy

import config
import geo
import math
import my_time

import album

from my_package import Package
from truck import Truck
import truck


def add_singular_plural_packages_as_needed(number):
    if number == 1:
        return f"{number} package"
    else:
        return f"{number} packages"


def round_float_to_tenths_for_display(f: float):
    return str(round(f, 1))


def right_pad_to_n_chars(s: str, n: int):
    if not s:
        return '               '
    s = str(s)
    if len(s) > n:
        return s[slice(0, n)]
    else:
        while len(s) < n:
            s += ' '
        return s


def bold_text(s: str):
    return '\u001b[37;1m' + s + '\u001b[0m'


def unpack_package_ids(list_of_p_ids):
    if not list_of_p_ids:
        return ''
    string = ''
    for p_id in list_of_p_ids:
        string += '#' + str(p_id) + ", "
    return string[:-2]


class Snapshot:
    def __init__(self, current_time_as_offset) -> None:
        self.current_time_as_offset: int = current_time_as_offset
        self.current_time_as_display: str = ''

        self.trucks = [None, None, None] # skip zeroth element so that truck numbers are indexes
        self.package_statuses = [None] * 41 # skip zeroth element so that package ids are indexes

        # computed values
        self.all_trucks_cumulative_mileage_for_day = 0.0

        self.is_key_frame = False
        

    def expand_truck_base_statuses_to_detailed_statuses(self):

        # truck statuses
        for truck_num in [1, 2]:
            if not self.trucks[truck_num]:
                continue
            if self.trucks[truck_num].base_status == 'at hub':
                self.trucks[truck_num].detailed_status = f"at hub (traveled {round_float_to_tenths_for_display(self.trucks[truck_num].cumulative_mileage_for_the_day)} miles so far today)"
            elif self.trucks[truck_num].base_status == 'back at hub':
                self.trucks[truck_num].detailed_status = f"back at hub (traveled {round_float_to_tenths_for_display(self.trucks[truck_num].cumulative_mileage_for_the_day)} miles so far today)"
            elif self.trucks[truck_num].base_status == 'departing hub':
                self.trucks[truck_num].detailed_status = f"departing hub with {add_singular_plural_packages_as_needed(self.trucks[truck_num].cur_num_pkgs)}"
            elif self.trucks[truck_num].base_status == 'en route':
                self.trucks[truck_num].detailed_status = f"en route with {add_singular_plural_packages_as_needed(self.trucks[truck_num].cur_num_pkgs)} ({round_float_to_tenths_for_display(self.trucks[truck_num].mileage_for_this_route_so_far)} miles traveled since hub)"
            elif self.trucks[truck_num].base_status == 'delivering':
                self.trucks[truck_num].detailed_status = f"delivering {add_singular_plural_packages_as_needed(self.trucks[truck_num].num_pkgs_being_delivered_now)} ({unpack_package_ids(self.trucks[truck_num].list_of_packages_delivered_to_this_stop)}) to {self.trucks[truck_num].cur_stop_street_address}"
            elif self.trucks[truck_num].base_status == 'last stop':
                self.trucks[truck_num].detailed_status = f"delivering {add_singular_plural_packages_as_needed(self.trucks[truck_num].num_pkgs_being_delivered_now)} ({unpack_package_ids(self.trucks[truck_num].list_of_packages_delivered_to_this_stop)}) to {self.trucks[truck_num].cur_stop_street_address}"
            elif self.trucks[truck_num].base_status == 'returning':
                self.trucks[truck_num].detailed_status = f"returning to hub empty ({round_float_to_tenths_for_display(self.trucks[truck_num].mileage_for_this_route_so_far)} miles traveled since hub)"
        


    def display(self):

        # construct package status lines
        all_package_statuses = ''
        for row_num in range(1, 11):
            if row_num == 10:
                cur_row = ''
            else:
                cur_row = ' '
            for pkg_ids_this_row in range(0, 31, 10):
                cur_row += f"{str(row_num + pkg_ids_this_row)} {right_pad_to_n_chars(self.package_statuses[row_num + pkg_ids_this_row], 15)}  "
            all_package_statuses += cur_row
            all_package_statuses += '\n'

        print(f""
        f"==============================================================================\n"
        f"Delivery Log Inspector for WGU package delivery system\n\n"
        f"Current time: {bold_text(right_pad_to_n_chars(my_time.convert_minutes_offset_to_time(self.current_time_as_offset), 8))}    Commands: 't': go to time,  'p' play,  'q': quit\n"
        f"                                    'a': ← 1 hr,  's': ← 10 min,  'd': ← 1 min\n"
        f"All trucks mileage so far: {right_pad_to_n_chars(str(round_float_to_tenths_for_display(self.all_trucks_cumulative_mileage_for_day) + ' mi'), 8)} 'j': → 1 min,  'k': → 10 min,  'l': → 1 hr\n"
        f"T# Status\n"
        f"-- ---------------------------------------------------------------------------\n"
        f" 1 {self.trucks[1].detailed_status}\n"
        f" 2 {self.trucks[2].detailed_status}\n"
        f" \n"
        f"P# Status           P# Status           P# Status           P# Status         \n"
        f"-- ---------------  -- ---------------  -- ---------------  -- ---------------\n"
        f"{all_package_statuses}"
        f"")
        
