import os
import time

import my_time

from album import Album
from my_time import parse_user_time as parse_user_time

def clear_screen():
    if os.name == 'posix':
        _ = os.system('clear')  # Mac and Linux
    else:
        _ = os.system('cls')  # Windows


def press_any_key():
    if os.name == 'posix':  # Mac and Linux
        _ = os.system('read -s -n 1 -p "Press any key to continue..."')
    else:  # Windows
        _ = os.system('pause')


def user_interface(album: Album):
    press_any_key()
    clear_screen()
    print(f"The delivery log contains {album.final_return_to_hub_as_offset} minutes of data, from 7:59 am to {my_time.offset_to_time(album.final_return_to_hub_as_offset)}.\n")
    
    cur_offset = -1
    
    while True:
        album.snapshots[cur_offset].display()

        cmd = input("Command ('q' to quit): ")
        offset_adjustment_cmds = {'a': -60, 's': -10, 'd': -1, 'j': 1, 'k': 10, 'l': 60}
        
        if cmd == 'q':
            break
        elif cmd in offset_adjustment_cmds.keys():
            cur_offset += offset_adjustment_cmds[cmd]
        elif cmd == 't':
            user_requested_time_str = input("Enter a time: ")
            user_requested_time_str_sanitized = parse_user_time(user_requested_time_str)
            user_requested_offset = my_time.time_to_offset(user_requested_time_str_sanitized)
            cur_offset = user_requested_offset
        elif cmd == 'p':
            cur_offset = -1
            while cur_offset < album.final_return_to_hub_as_offset:
                clear_screen()
                album.snapshots[cur_offset].display()
                
                if album.snapshots[cur_offset].trucks[1].detailed_status.startswith('de') or album.snapshots[cur_offset].trucks[2].detailed_status.startswith('de'):  # will catch both 'departing' and 'delivering'
                    time.sleep(3)
                elif cur_offset == -1:
                    time.sleep(3)
                else:
                    time.sleep(0.25)
                
                cur_offset += 1
            cur_offset = album.final_return_to_hub_as_offset
        else:
            print("")

         # bounds checking
        if cur_offset < -1:
            cur_offset = -1
        elif cur_offset > album.final_return_to_hub_as_offset:
            cur_offset = album.final_return_to_hub_as_offset 
        
        clear_screen()