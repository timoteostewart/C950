import os
import re
import time

from album import Album
import my_time

def clear_screen():
    if os.name == 'posix':
        _ = os.system('clear') # Mac and Linux
    else:
        _ = os.system('cls') # Windows

def press_any_key():
    # print(f"Press any key to continue...")
    if os.name == 'posix': # Mac and Linux
        _ = os.system('read -s -n 1 -p "Press any key to continue..."')
    else: # Windows
        _ = os.system('pause')


def parse_user_time(time_as_str):
    am_designator_re = [r'.*(a[\.\ ]?[\ ]?m[\.\ ]?).*', r'.*(a[\.]?).*']
    pm_designator_re = [r'.*(p[\.\ ]?[\ ]?m[\.\ ]?).*', r'.*(p[\.]?).*']
    
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
        hour = 24
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
        ampmdesignator = "a.m."
    elif is_pm and not is_am:
        ampmdesignator = "p.m."
    else: # (is_am and is_pm) or (not is_am and not is_pm):
        ampmdesignator = "a.m."

    # display checks
    if minute < 10:
        minute = '0' + str(minute)

    return f"{hour}:{minute} {ampmdesignator}"


def user_interface(album: Album):
    press_any_key()
    clear_screen()
    print(f"The delivery log contains {album.final_return_to_hub_as_offset} minutes of data, from 7:59 am to {my_time.convert_minutes_offset_to_time(album.final_return_to_hub_as_offset)}.\n")
    
    cur_offset = -1
    
    while True:
        album.snapshots[cur_offset].display()
        cmd = input("Command ('q' to quit): ")
        # print(f"received {cmd} command")

        offset_adjustment_cmds = {'a': -60, 's': -10, 'd': -1, 'j': 1, 'k': 10, 'l': 60}
        
        if cmd == 'q':
            break
        elif cmd in offset_adjustment_cmds.keys():
            cur_offset += offset_adjustment_cmds[cmd]
            if cur_offset < -1:
                cur_offset = -1
            elif cur_offset > album.final_return_to_hub_as_offset:
                cur_offset = album.final_return_to_hub_as_offset 
        elif cmd == 't':
            user_time_str = input("Enter a time:")
            cur_offset = parse_time(user_time_str)
        elif cmd == 'p':
            cur_offset = -1
            while cur_offset < album.final_return_to_hub_as_offset:
                clear_screen()
                album.snapshots[cur_offset].display()
                
                if album.snapshots[cur_offset].trucks[1].detailed_status.startswith('de') or album.snapshots[cur_offset].trucks[2].detailed_status.startswith('de'): # will catch 'departing' and 'delivering'
                    time.sleep(3)
                elif cur_offset == -1:
                    time.sleep(3)
                else:
                    time.sleep(0.25)
                
                cur_offset += 1
            cur_offset = album.final_return_to_hub_as_offset
        else:
            print("")
        clear_screen()