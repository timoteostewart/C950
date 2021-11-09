import config

class Truck:

    def __init__(self, name):
        self.name = name
        self.bill_of_lading = [] # in delivery order
        self.delivery_zips = set()
        self.time_on_road = 0.0
    
    def add_package(self, package_id):

        # update delivery_zips
        self.delivery_zips.add(config.all_packages_by_id_ht.get_or_default(package_id).zip)

        # update truck's total time on the road, including return to hub
        ## TODO
        ## subtract time from last package to hub
        # add time from last package to new package
        # add time from new package to hub
        # update `self.time_on_road`
        
        
        # self.bill_of_lading.append(package_id)

