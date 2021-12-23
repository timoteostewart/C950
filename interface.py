import os

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


def user_interface(album: Album):
   press_any_key()
   clear_screen()
   print(f"The album contains {album.final_return_to_hub_as_offset} minutes of data, from 7:59 am to {my_time.convert_minutes_offset_to_time(album.final_return_to_hub_as_offset)}.")
   
   while True:
      cmd = input("Command ('q' to quit): ")
      print(f"received {cmd} command")
      if cmd == 'q':
         break