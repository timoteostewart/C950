import config
import geo
import my_time

class Truck:

    MINUTES_PER_MILE = 3.3333

    def __init__(self, name):
        self.name = name

        self.bill_of_lading = [] # in delivery order
        self.delivery_zips = set()
        self.start_time_this_run = '8:00 am' # default is 8:00 am
        self.finish_time_this_run = ''
        self.time_on_road_this_run = 0.0 # in minutes
        self.distance_on_road_this_run = 0.0 # in miles
        self.delivery_log = []

        self.time_on_road_today = 0.0 # in minutes
        self.distance_on_road_today = 0.0 # in miles

    def end_run(self):
        # update fields
        self.time_on_road_today += self.time_on_road_this_run
        self.distance_on_road_today += self.distance_on_road_this_run

        self.finish_time_this_run = my_time.add_minutes_to_clock_time(self.start_time_this_run, self.time_on_road_this_run)

        # store global stats
        config.master_delivery_log.append(self.delivery_log)
        config.hub_stats_miles += self.distance_on_road_this_run

        print(f"{self.name}: started {self.start_time_this_run}, finished {self.finish_time_this_run}, miles {self.distance_on_road_this_run}, packages {len(self.delivery_log)}: {self.delivery_log}")

        # reset truck object
        self.bill_of_lading = [] # in delivery order
        self.delivery_zips = set()
        self.start_time_this_run = self.finish_time_this_run
        self.finish_time_this_run = ''
        self.time_on_road_this_run = 0.0 # in minutes
        self.distance_on_road_this_run = 0.0 # in miles
        self.delivery_log = []


    def add_package_to_delivery_log(self, package_id):
        delivery_as_offset = self.distance_on_road_this_run * self.MINUTES_PER_MILE + my_time.convert_time_to_minutes_offset(self.start_time_this_run)
        cur_time = my_time.convert_minutes_offset_to_time(delivery_as_offset)
        log_entry = (package_id, cur_time)
        self.delivery_log.append(log_entry)
        if delivery_as_offset > config.all_packages_by_id[package_id].deadline:
            print(f"package {package_id} was late!")


    def update_time_on_road(self):
        self.delivery_log = []
        self.distance_on_road_this_run = 0.0
        if len(self.bill_of_lading) == 0: # no packages
            pass
        else: # at least 1 package
            first_address = config.all_packages_by_id[self.bill_of_lading[0]].street_address
            self.distance_on_road_this_run += geo.get_distance(geo.HUB_STREET_ADDRESS, first_address)
            self.add_package_to_delivery_log(self.bill_of_lading[0])

            if len(self.bill_of_lading) == 1: # exactly 1 package
                pass
            else: # 2 or more packages
                for i in range(1, len(self.bill_of_lading)):
                    prev_street_address = config.all_packages_by_id[self.bill_of_lading[i - 1]].street_address
                    cur_street_address = config.all_packages_by_id[self.bill_of_lading[i]].street_address
                    self.distance_on_road_this_run += geo.get_distance(prev_street_address, cur_street_address)
                    self.add_package_to_delivery_log(self.bill_of_lading[i])

            # return to hub
            last_address = config.all_packages_by_id[self.bill_of_lading[-1]].street_address
            self.distance_on_road_this_run += geo.get_distance(last_address, geo.HUB_STREET_ADDRESS)
                

        self.time_on_road_this_run = self.distance_on_road_this_run * self.MINUTES_PER_MILE

    def add_package(self, package_id):
        if config.all_packages_by_id[package_id].when_can_leave_hub > my_time.convert_time_to_minutes_offset(self.start_time_this_run):
            print(f"package id {package_id} can't leave yet!")
            
        self.bill_of_lading.append(package_id)
        self.delivery_zips.add(config.all_packages_by_id[package_id].zip)
        self.update_time_on_road()
        try:
            config.packages_at_hub.remove(package_id)
        except ValueError:
            print(f"{package_id} can't be removed")
    
    def add_packages(self, list_ids):
        for id in list_ids:
            self.add_package(id)

