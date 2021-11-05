
def convert_time_to_minutes_offset(time):
    colon_offset = time.find(':')
    space_offset = time.find(' ')
    clock_hours = time[0:colon_offset]
    clock_minutes = time[colon_offset + 1:space_offset]
    offset_in_minutes = (int(clock_hours) - 8) * 60 + int(clock_minutes)
    return offset_in_minutes

def convert_minutes_offset_to_time(offset_in_minutes):
    clock_minutes = offset_in_minutes % 60
    clock_hours = 8 + offset_in_minutes // 60 # round down (floor)
    if clock_minutes < 10:
        return f"{clock_hours}:0{clock_minutes} am"
    else:
        return f"{clock_hours}:{clock_minutes} am"