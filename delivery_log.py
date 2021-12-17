class DeliveryLog:

    def print_status_of_all_packages(self, time_as_offset):
        pass


"""
Delivery Log Inspector for WGU package delivery system
Current time: 00:00 am    Commands: 't': go to time,  'p' play,  'q': quit
All trucks mileage so far: 000.0    'a': ← 1 hr,  's': ← 10 min,  'd': ← 1 min
T# Status                           'j': → 1 min,  'k': → 10 min,  'l': → 1 hr
-- ---------------------------------------------------------------------------
 1 at hub (traveled 42.1 miles so far today)
 1 departing hub with 16 packages
 1 en route with 15 packages (traveled 0.0 miles since hub)
 2 en route with 2 packages
 1 delivering 2 pkgs at 3575 W Valley Central Station Bus Loop
 2 returning to hub empty (traveled 0.0 miles since hub)

P# Status           P# Status           P# Status           P# Status         
-- ---------------  -- ---------------  -- ---------------  -- ---------------
 1 not yet at hub   11                  21                  31 
 2 at the hub       12                  22                  32
 3 en route, trk 0  13                  23                  33
 4 being dlvrd now  14                  24                  34
 5 dlvrd @00:00 am  15                  25                  35
 6 added to trk 0   16                  26                  36
 7                  17                  27                  37
 8                  18                  28                  38
 9 incorrect addr.  19                  29                  39
10                  20                  30                  40


"""