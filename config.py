from hash_table import HashTable

HASH_TABLE_LOAD_FACTOR = 0.75

MINUTES_PER_MILE = 3.3333 #  = 60 minutes per 18 miles
MILES_PER_MINUTE = 0.3 # 18 miles per 60 minutes

all_packages_by_id = [None] * 41
distances_between_pairs = HashTable(729 // HASH_TABLE_LOAD_FACTOR) # 27 possible stops, so we'll store 729 (= 27²) location pairs
all_stops_by_street_address = HashTable(27 // HASH_TABLE_LOAD_FACTOR) # 27 possible stops

master_delivery_log = []
route_lists = []


