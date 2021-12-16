import math

def convert_time_to_minutes_offset(time):
    colon_offset = time.find(':')
    space_offset = time.find(' ')
    clock_hours = int(time[0:colon_offset])
    if 'pm' in time:
        clock_hours += 12
    clock_minutes = int(time[colon_offset + 1:space_offset])
    offset_in_minutes = (clock_hours - 8) * 60 + clock_minutes
    return offset_in_minutes

def convert_minutes_offset_to_time(offset_in_minutes):
    clock_minutes = int(math.ceil(offset_in_minutes)) % 60
    clock_hours = int(8 + math.floor(offset_in_minutes / 60))

    if clock_hours > 12:
        ampm = 'pm'
        clock_hours -= 12
    elif clock_hours == 12:
        ampm = 'pm'
    else:
        ampm = 'am'

    if clock_minutes < 10:
        return f"{clock_hours}:0{clock_minutes} {ampm}"
    else:
        return f"{clock_hours}:{clock_minutes} {ampm}"
