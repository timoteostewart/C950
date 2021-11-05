import config

class Location:

    def __init__(self, capacity):
        pass


def distance_squared_between_zips(zip1, zip2):
    x1, y1 = relative_zip_coords(zip1)
    x2, y2 = relative_zip_coords(zip2)
    return (x2 - x1) ** 2 + (y2 - y1) ** 2 # no need for us to compute square root


def relative_zip_coords(zip):
    if zip == '84103':
        return (2, 0)
    elif zip == '84104':
        return (1, 1)
    elif zip == '84105':
        return (3, 1)
    elif zip == '84106':
        return (3, 2)
    elif zip == '84107':
        return (2, 3)
    elif zip == '84111':
        return (2, 1)
    elif zip == '84115':
        return (2, 2)
    elif zip == '84117':
        return (3, 3)
    elif zip == '84118':
        return (0, 3)
    elif zip == '84119':
        return (1, 2)
    elif zip == '84121':
        return (4, 3)
    elif zip == '84123':
        return (1, 3)
    else:
        raise ValueError("unrecognized zip code!")

def return_package_id_of_westmost_delivery_address(list_of_packages):
    cur_greatest_distance = 0
    cur_package_id = 0

    for x in list_of_packages:
        cur_distance = distance_squared_between_zips(config.all_packages_by_id_ht(x).zip)

def return_package_id_of_eastmost_delivery_address(list_of_packages):
    pass
