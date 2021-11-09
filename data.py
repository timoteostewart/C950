import csv
import re

import config
import my_time

from hash_table import HashTable
from package import Package

# declare hash tables
HASH_TABLE_LOAD_FACTOR = 0.75 # plan is for hash tables to use up to 75% of their maximum capacity
all_addresses_ht = HashTable(int(26 // HASH_TABLE_LOAD_FACTOR)) # there are 26 street addresses
all_packages_ht = HashTable(int(40 // HASH_TABLE_LOAD_FACTOR)) # there are 40 packages
distances_ht = HashTable(int(351 // HASH_TABLE_LOAD_FACTOR)) # there are 351 location pairs; hash table unit is miles
# travel_time_ht = HashTable(int(351 // HASH_TABLE_LOAD_FACTOR)) # 351 location pairs; hash table unit is minutes of travel time


def ingest_distances():

    list_of_locations = []

    with open('WGUPS Distance Table.csv') as csvfile:
        distances = csv.reader(csvfile, delimiter=',')
        for row in distances:
            if row[0] != '' and row[1] != '' and ord(row[0][0]) <= 90:
                left_location = row[1]
                if left_location == "HUB":
                    left_location = "4001 South 700 East"
                else:
                    left_location = left_location[:-8] # strip out trailing parenthetical zip code
                list_of_locations.append(left_location)

    with open('WGUPS Distance Table.csv') as csvfile:
        distances = csv.reader(csvfile, delimiter=',')
        cur_row = 0
        for row in distances:
            if row[0] != '' and row[1] != '' and ord(row[0][0]) <= 90:
                    
                left_location = list_of_locations[cur_row]
                cur_row += 1

                for col in range(2, 29):
                    distance = row[col]
                    if distance == '':
                        continue
                    
                    right_location = list_of_locations[col - 2]

                    K = f"{left_location} and {right_location}"
                    V = distance

                    if left_location == right_location:
                        config.distances_between_pairs.add(K, V)
                    else:
                        K2 = f"{right_location} and {left_location}"
                        config.distances_between_pairs.add(K, V)
                        config.distances_between_pairs.add(K2, V)
                    
                    # print(f"{left_location} and {right_location}: {distance} ", end='\n')
                    # config.distances_between_pairs.add(K, V)
                        

def ingest_packages():

    with open('WGUPS Package File.csv') as csvfile:
        distances = csv.reader(csvfile, delimiter=',')
        for row in distances:
            state = row[3]
            if state != 'UT': # skip header rows that precede package data rows
                continue

            package_id = int(row[0])
            street_address = row[1]
            city = row[2]
            zip = str(row[4])
            deadline = row[5]
            weight_kg = int(row[6])
            notes = row[7]

            # compute deadline
            if deadline == 'EOD':
                deadline = 1440 # 1440 minutes = 24 hours * 60 minutes
            else:
                deadline = my_time.convert_time_to_minutes_offset(deadline)

            when_can_leave_hub = 0
            package_affinities = {0}
            truck_affinity = 0

            if notes:
                if "Can only be on truck" in notes:
                    pattern = r'truck ([\d]+)'
                    a = re.search(pattern, notes)
                    if a:
                        # print(f"affinity to truck {a.group(1)}")
                        truck_affinity = 'truck ' + a.group(1)
                if "Delayed on flight" in notes:
                    # print("is delayed on flight")
                    pattern = r'until ([0-9:\ am]+)'
                    a = re.search(pattern, notes)
                    if a:
                        # print(f"late flight; delayed until {a.group(1)}")
                        when_can_leave_hub = my_time.convert_time_to_minutes_offset(a.group(1))
                if "Wrong address listed" in notes:
                    # print("is on hold at hub")
                    pattern = r'until ([0-9:\ am]+)'
                    a = re.search(pattern, notes)
                    if a:
                        # print(f"wrong address; delayed until {a.group(1)}")
                        when_can_leave_hub = my_time.convert_time_to_minutes_offset(a.group(1))
                if "Must be delivered with" in notes:
                    pattern = r'\b([\d]+)\b'
                    a = re.findall(pattern, notes)
                    if a:
                        a_list = [package_id]
                        for num in a:
                            a_list.append(int(num))
                        # a_list.sort()
                        package_affinities = set(a_list)

            current_package = Package(package_id, street_address, zip, deadline, weight_kg, notes, when_can_leave_hub, package_affinities, truck_affinity)

            config.all_packages_by_id_ht.add(str(package_id), current_package)
            # all_addresses_ht.add(street_address, zip)
            # all_packages_by_zip.add(zip, package_id)
            config.all_packages_by_zip[zip].append(package_id)
            
            # print(current_package)
            config.hub_package_list.append(current_package.id)

