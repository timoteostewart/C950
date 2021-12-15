# from _typeshed import NoneType
from collections import defaultdict

from hash_table import HashTable

HASH_TABLE_LOAD_FACTOR = 0.75

MINUTES_PER_MILE = 3.3333 #  = 60 minutes per 18 miles
MILES_PER_MINUTE = 0.3 # 18 miles per 60 minutes



# all_packages_by_id_ht = HashTable(40 // HASH_TABLE_LOAD_FACTOR) # 40 distinct packages
all_packages_by_id = [None] * 41
# all_packages_by_zip = defaultdict(list) # 12 distinct delivery codes
distances_between_pairs = HashTable(729 // HASH_TABLE_LOAD_FACTOR) # 27 possible stops, so we'll store 729 (= 27²) location pairs
all_stops_by_street_address = HashTable(27 // HASH_TABLE_LOAD_FACTOR) # 27 possible stops

stops_near_hub = [] # "near" means 3.6 miles from hub or closer

packages_at_hub = []
packages_delivered = []

master_delivery_log = []

hub_stats_miles = 0.0

pkgs_eight_oclock_all = None

cumulative_miles = 0

route_lists = []

count = 0

failed_route_lists = 0

failure_reasons = {}
failure_reasons['took too long'] = 0
failure_reasons['late packages'] = 0
failure_reasons['route mileage too high'] = 0
failure_reasons['route mileage infinite'] = 0
failure_reasons['did not beat current winner'] = 0

route_lists_that_hit_zero_pkgs = 0

forty = [0] * 41
came_in_left_with_1 = [list(forty)] * 41
came_in_left_with_2 = [list(forty)] * 41

fewest_packages_seen = 40

found_a_solution = False