from pyparrot.Bebop import Bebop
import math
import signal

#function that gets called when ctrl+C interrupt occurs
def handler(signum, frame):
    bebop.safe_land(10)

    print("DONE - disconnecting")
    bebop.disconnect()
    exit(1)

#connects the ctrl+C interrupt to the function
signal.signal(signal.SIGINT, handler)

bebop = Bebop()
print("connecting")
success = bebop.connect(10)
print(success)

#Desired location to travel to
lat = 39.96166130276774
lon = -75.18769108889548

loc_radians = math.atan(lat/lon)

print("sleeping")
bebop.smart_sleep(5)

bebop.safe_takeoff(10)
bebop.smart_sleep(2)

print("Start Move Up")
bebop.move_relative(0,0,-1,0)

Lat_Start = bebop.sensors.sensors_dict["GpsLocationChanged_latitude"]
Lon_Start = bebop.sensors.sensors_dict["GpsLocationChanged_longitude"]
dlat_loc = lat - Lat_Start
dlon_loc = lon - Lon_Start
loc_radians = math.atan(dlat_loc/dlon_loc)

if(dlon_loc < 0):
    loc_radians += math.pi

print("Start Moving")
bebop.move_relative(2, 0, 0, 0)
Lat_End = bebop.sensors.sensors_dict["GpsLocationChanged_latitude"]
Lon_End = bebop.sensors.sensors_dict["GpsLocationChanged_longitude"]
print("Done Moving")

dlat = Lat_End - Lat_Start
dlon = Lon_End - Lon_Start
current_radians = math.atan(dlat/dlon)

if(dlon < 0):
    current_radians += math.pi

difference_radians = loc_radians - current_radians
print(difference_radians)
bebop.move_relative(0,0,0,-difference_radians)

bebop.safe_land(10)

print("DONE - disconnecting")
bebop.disconnect()

