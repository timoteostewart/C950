import csv
import re

import my_time

from hash_table import HashTable
from package import Package

# declare hash tables
HASH_TABLE_LOAD_FACTOR = 0.75 # plan is for hash tables to use up to 75% of their maximum capacity
all_addresses_ht = HashTable(int(26 / HASH_TABLE_LOAD_FACTOR)) # there are 26 street addresses
all_packages_ht = HashTable(int(40 / HASH_TABLE_LOAD_FACTOR)) # there are 40 packages
distances_ht = HashTable(int(351 / HASH_TABLE_LOAD_FACTOR)) # there are 351 location pairs; hash table unit is miles
travel_time_ht = HashTable(int(351 / HASH_TABLE_LOAD_FACTOR)) # 351 location pairs; hash table unit is minutes of travel time


def ingest_distances():
    with open('WGUPS Distance Table.csv') as csvfile:
        distances = csv.reader(csvfile, delimiter=',')
        for row in distances:
            print(', '.join(row))
                    

def ingest_packages(all_packages_by_id_ht, all_packages_by_zip, hub_package_list):
    global all_addresses_ht

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
                        truck_affinity = a.group(1)
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

            all_packages_by_id_ht.add(str(package_id), current_package)
            # all_addresses_ht.add(street_address, zip)
            # all_packages_by_zip.add(zip, package_id)
            all_packages_by_zip[zip].append(package_id)
            
            # print(current_package)
            hub_package_list.append(current_package.id)

