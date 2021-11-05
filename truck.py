class Truck:

    def __init__(self, name):
        self.name = name
        self.bill_of_lading = []
        self.delivery_zips = set()
        self.id_of_first_package_to_deliver = 0