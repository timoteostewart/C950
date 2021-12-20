import os

from album import Album

def screen_clear():
   if os.name == 'posix':
      _ = os.system('clear') # Mac and Linux
   else:
      _ = os.system('cls') # Windows


def user_interface(album: Album):
    print("hi!")
    pass