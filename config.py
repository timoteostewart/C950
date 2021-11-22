# from _typeshed import NoneType
from collections import defaultdict

from hash_table import HashTable

HASH_TABLE_LOAD_FACTOR = 0.75

MINUTES_PER_MILE = 3.3333 #  = 60 minutes per 18 miles
MILES_PER_MINUTE = 0.3 # 18 miles per 60 minutes
HUB_STREET_ADDRESS = '4001 S 700 East'
HUB_LAT_LONG = (40.685116081559286, -111.86998980967073)

# all_packages_by_id_ht = HashTable(40 // HASH_TABLE_LOAD_FACTOR) # 40 distinct packages
all_packages_by_id = [None] * 41
# all_packages_by_zip = defaultdict(list) # 12 distinct delivery codes
distances_between_pairs = HashTable(729 // HASH_TABLE_LOAD_FACTOR) # 27 possible stops, so we'll store 729 (= 27²) location pairs
all_stops_by_street_address = HashTable(27 // HASH_TABLE_LOAD_FACTOR) # 27 possible stops

packages_at_hub = []
packages_delivered = []

master_delivery_log = []

hub_stats_miles = 0.0


