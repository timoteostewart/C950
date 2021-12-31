from hash_table import HashTable

HASH_TABLE_LOAD_FACTOR = 0.75

MINUTES_PER_MILE = 3.3333  #  = 60 minutes per 18 miles
MILES_PER_MINUTE = 0.3  # 18 miles per 60 minutes

distances_between_pairs_ht = HashTable((27 ** 2) // HASH_TABLE_LOAD_FACTOR)  # 27 possible stops, so we'll store 27² (== 729) location pairs
all_stops_by_street_address_ht = HashTable(27 // HASH_TABLE_LOAD_FACTOR)  # 27 possible stops
all_packages_by_id_ht = HashTable(40 // HASH_TABLE_LOAD_FACTOR)  # 40 packages

route_lists = []  # to store valid route_lists during backtracking algorithm
