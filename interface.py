import os

def screen_clear():
   if os.name == 'posix':
      _ = os.system('clear') # Mac and Linux
   else:
      _ = os.system('cls') # Windows


def interface_loop():
    print("hi!")
    pass