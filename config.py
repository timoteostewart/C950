from collections import defaultdict

from hash_table import HashTable

all_packages_by_id_ht = HashTable(60)
all_packages_by_zip = defaultdict(list) # 12 distinct delivery codes

hub_package_list = []
delivered_list = []

zips_from_west_to_east = [84118, 84123, 84119, 84104, 84103, 84111, 84115, 84117, 84106, 84105, 84121]