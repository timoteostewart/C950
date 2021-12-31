import math
import re

def time_to_offset(time):
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


def offset_to_time(offset_in_minutes):
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


def parse_user_time(time_as_str):
    am_designator_re = [r'.*(a[\.]?[\ ]?m[\.]?).*', r'.*(a[\.]?).*']
    pm_designator_re = [r'.*(p[\.]?[\ ]?m[\.]?).*', r'.*(p[\.]?).*']
    time_values_re = [r'([\d]{1,2})[^\d]*([\d]{2})', r'[\d]{1,2}']

    is_am = False
    is_pm = False
    ampmdesignator = None
    hour = None
    minute = None

    # check for am
    for r in am_designator_re:
        result = re.match(r, time_as_str, re.IGNORECASE)
        if result:
            is_am = True
    
    # check for pm
    for r in pm_designator_re:
        result = re.match(r, time_as_str, re.IGNORECASE)
        if result:
            is_pm = True

    for r in time_values_re:
        result = re.findall(r, time_as_str)
        if result:
            if type(result[0]) == tuple:
                hour = int(result[0][0])
                minute = int(result[0][1])
                break
            else:
                hour = int(result[0])
                minute = 0
    
    # bounds checking
    # hours
    if hour is None or hour <= 0:
        hour = 12
        is_am = True
        is_pm = False
    if hour > 24:
        hour = hour % 24
    if hour > 12:
        is_am = False
        is_pm = True
        hour -= 12
    # minutes
    if minute is None or minute < 0:
        minute = 0
    elif minute > 59:
        minute = 59

    # assign am/pm designator
    if is_am and not is_pm:
        ampmdesignator = "am"
    elif is_pm and not is_am:
        ampmdesignator = "pm"
    else: # (is_am and is_pm) or (not is_am and not is_pm):
        if hour == 12:
            ampmdesignator = "pm"
        else:
            ampmdesignator = "am"

    # display checks
    if minute < 10:
        minute = '0' + str(minute)

    return f"{hour}:{minute} {ampmdesignator}"