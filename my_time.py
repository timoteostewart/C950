import math

def convert_time_to_minutes_offset(time):
    colon_offset = time.find(':')
    space_offset = time.find(' ')
    hour = int(time[0:colon_offset])
    minute = int(time[colon_offset + 1:space_offset])

    if 'am' in time and hour == 12:
        hour = 0
    
    if 'pm' in time and hour < 12:
        hour += 12
    
    offset_in_minutes = (hour - 8) * 60 + minute
    return offset_in_minutes


def convert_minutes_offset_to_time(offset_in_minutes):
    minute = offset_in_minutes % 60
    hour = 8 + int(math.floor(offset_in_minutes / 60))

    if hour > 12:
        ampmdesignator = 'pm'
        hour -= 12
    elif hour == 12:
        ampmdesignator = 'pm'
    else:
        ampmdesignator = 'am'

    if minute < 10:
        minute = '0' + str(minute)

    return f"{hour}:{minute} {ampmdesignator}"
