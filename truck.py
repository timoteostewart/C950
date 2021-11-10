import config
import data
import my_time

class Truck:

    MINUTES_PER_MILE = 3.3333

    def __init__(self, name):
        self.name = name
        self.bill_of_lading = [] # in delivery order
        self.delivery_zips = set()
        self.start_time_this_run = '8:00 am' # default is 8:00 am
        self.time_on_road_this_run = 0.0 # in minutes
        self.time_on_road_today = 0.0 # in minutes
        self.distance_on_road_this_run = 0.0 # in miles
        self.distance_on_road_today = 0.0 # in miles
        self.delivery_log = []

    def end_run(self):
        self.time_on_road_today += self.time_on_road_this_run
        self.distance_on_road_today += self.distance_on_road_this_run
        config.master_delivery_log.append(self.delivery_log)

        self.bill_of_lading = [] # in delivery order
        self.delivery_zips = set()
        self.time_on_road_this_run = 0.0 # in minutes
        self.distance_on_road_this_run = 0.0 # in miles
        self.delivery_log = []

    def add_package_to_delivery_log(self, package_id):
        cur_time = my_time.convert_minutes_offset_to_time(self.distance_on_road_this_run * self.MINUTES_PER_MILE + my_time.convert_time_to_minutes_offset(self.start_time_this_run))
        log_entry = (package_id, cur_time)
        self.delivery_log.append(log_entry)

    def update_time_on_road(self):
        self.delivery_log = []
        self.distance_on_road_this_run = self.distance_on_road_today
        if len(self.bill_of_lading) == 0: # no packages
            pass
        else: # at least 1 package
            first_address = config.all_packages_by_id[self.bill_of_lading[0]].street_address
            self.distance_on_road_this_run += data.get_distance(config.HUB_STREET_ADDRESS, first_address)
            self.add_package_to_delivery_log(self.bill_of_lading[0])

            if len(self.bill_of_lading) == 1: # exactly 1 package
                pass
            else: # 2 or more packages
                for i in range(1, len(self.bill_of_lading)):
                    prev_street_address = config.all_packages_by_id[self.bill_of_lading[i - 1]].street_address
                    cur_street_address = config.all_packages_by_id[self.bill_of_lading[i]].street_address
                    self.distance_on_road_this_run += data.get_distance(prev_street_address, cur_street_address)
                    self.add_package_to_delivery_log(self.bill_of_lading[i])

            # return to hub
            last_address = config.all_packages_by_id[self.bill_of_lading[-1]].street_address
            self.distance_on_road_this_run += data.get_distance(last_address, config.HUB_STREET_ADDRESS)
                

        self.time_on_road_this_run = self.time_on_road_today + self.distance_on_road_this_run * self.MINUTES_PER_MILE

    def add_package(self, package_id):
        self.bill_of_lading.append(package_id)
        self.delivery_zips.add(config.all_packages_by_id[package_id].zip)
        self.update_time_on_road()

