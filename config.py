# from _typeshed import NoneType
from collections import defaultdict

from hash_table import HashTable

HASH_TABLE_LOAD_FACTOR = 0.75

MINUTES_PER_MILE = 3.3333 #  = 60 minutes per 18 miles
MILES_PER_MINUTE = 0.3 # 18 miles per 60 minutes
HUB_STREET_ADDRESS = '4001 South 700 East'

# all_packages_by_id_ht = HashTable(40 // HASH_TABLE_LOAD_FACTOR) # 40 distinct packages
all_packages_by_id = [None] * 41
distances_between_pairs = HashTable(729 // HASH_TABLE_LOAD_FACTOR) # 27 locations, so we'll store 729 (= 27²) location pairs
all_packages_by_zip = defaultdict(list) # 12 distinct delivery codes

hub_package_list = []
delivered_list = []

zips_from_west_to_east_rush = ['84117', '84118', '84123', '84119', '84104', '84103', '84111', '84115',  '84106', '84105', '84121'] # zip code with 9:00am deliveries is bumped to first place

zips_from_west_to_east_nonrush = ['84118', '84123', '84119', '84104', '84103', '84111', '84115', '84117', '84106', '84105', '84121']

master_delivery_log = []