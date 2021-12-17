import csv
import re

import config
import geo
import my_package
import my_time

def ingest_distances():
    # populate list_of_locations
    list_of_street_addresses = []
    with open('WGUPS Distance Table.csv') as csvfile:
        distances = csv.reader(csvfile, delimiter=',')
        for row in distances:
            if row[0] != '' and row[1] != '' and ord(row[0][0]) <= 90:
                # populate list_of_street_addresses
                street_address = row[1]
                street_address = street_address[:-8] # truncate parenthetical zip code
                list_of_street_addresses.append(street_address)

    # populate config.distances_between_pairs_ht
    with open('WGUPS Distance Table.csv') as csvfile:
        distances = csv.reader(csvfile, delimiter=',')
        cur_row = 0
        for row in distances:
            if row[0] != '' and row[1] != '' and ord(row[0][0]) <= 90:
                left_location = list_of_street_addresses[cur_row]
                cur_row += 1

                for col in range(2, 29):
                    distance = row[col]
                    if distance == '':
                        continue
                    right_location = list_of_street_addresses[col - 2]
                    K = f"{left_location} and {right_location}"
                    V = float(distance)
                    if left_location == right_location:
                        config.distances_between_pairs_ht.add(K, V)
                    else:
                        K2 = f"{right_location} and {left_location}"
                        config.distances_between_pairs_ht.add(K, V)
                        config.distances_between_pairs_ht.add(K2, V)
                        
    for street_address in list_of_street_addresses:
        # populate config.all_stops_by_street_address_ht
        cur_stop = geo.Stop(street_address, geo.get_distance(geo.HUB_STREET_ADDRESS, street_address))
        config.all_stops_by_street_address_ht.add(street_address, cur_stop)


def ingest_packages():
    packages_at_hub = []
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
            deadline_as_time = row[5]
            weight_kg = int(row[6])
            notes = row[7]

            # compute deadline as an offset
            deadline_as_offset = None # will initialize next
            if deadline_as_time == 'EOD':
                deadline_as_offset = 1440 # 1440 minutes = 24 hours * 60 minutes; this represents a deadline of "end of day"
            else:
                deadline_as_offset = my_time.convert_time_to_minutes_offset(deadline_as_time)

            when_can_leave_hub = 0
            package_affinities = {0} # a set representing the package id's of other packages that must be delivered with this package
            truck_affinity = '' # format is: 'truck 1' or 'truck 2'
            delivery_status = '' # will initialize below

            if notes:
                if "Can only be on truck" in notes:
                    pattern = r'(truck [\d]+)'
                    a = re.search(pattern, notes)
                    if a:
                        truck_affinity = str(a.group(1))
                if "Delayed on flight" in notes:
                    pattern = r'until ([0-9:\ am]+)'
                    a = re.search(pattern, notes)
                    if a:
                        when_can_leave_hub = my_time.convert_time_to_minutes_offset(a.group(1))
                        delivery_status = 'not yet at hub'
                if "Wrong address listed" in notes:
                    # print("is on hold at hub")
                    pattern = r'until ([0-9:\ am]+)'
                    a = re.search(pattern, notes)
                    if a:
                        when_can_leave_hub = my_time.convert_time_to_minutes_offset(a.group(1))
                        delivery_status = 'incorrect addr.'
                if "Must be delivered with" in notes:
                    pattern = r'\b([\d]+)\b'
                    a = re.findall(pattern, notes)
                    if a:
                        a_list = [package_id]
                        for num in a:
                            a_list.append(int(num))
                        package_affinities = set(a_list)

            distance_from_hub = geo.get_distance(geo.HUB_STREET_ADDRESS, street_address)

            if not delivery_status:
                # if we haven't assigned a special delivery status, default to 'at the hub'
                delivery_status = 'at the hub'

            # add this package to our hash table
            cur_package = my_package.Package(package_id, street_address, city, zip, deadline_as_offset, weight_kg, notes, when_can_leave_hub, package_affinities, truck_affinity, distance_from_hub, delivery_status)
            config.all_packages_by_id_ht.add(package_id, cur_package)
            
            packages_at_hub.append(cur_package)
    
    return packages_at_hub

