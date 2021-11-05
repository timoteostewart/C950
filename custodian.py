
class Custodian:

    def __init__(self, name, location, capacity):
        self.name = name
        self.location = location
        self.packages_in_custody = [] # by package_id
        self.capacity = capacity

    def accept_package(self, package_id):
        self.packages_in_custody.append(package_id)
        self.capacity += 1
    
    def surrender_package(self, package_id):
        self.packages_in_custody.remove(package_id)
        return package_id

    def is_full(self):
        if len(self.packages_in_custody) >= self.capacity:
            return True
        else:
            return False

    