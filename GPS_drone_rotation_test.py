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
lat = 39.961680
lon = -75.187586

loc_radians = math.atan(lat/lon)

print("sleeping")
bebop.smart_sleep(5)

bebop.safe_takeoff(10)


Lat_Start = bebop.sensors.sensors_dict["GpsLocationChanged_latitude"]
Lon_Start = bebop.sensors.sensors_dict["GpsLocationChanged_longitude"]
dlat_loc = lat - Lat_Start
dlon_loc = lon - Lon_Start
loc_radians = math.atan(dlat_loc/dlon_loc)
if(dlon_loc < 0):
    loc_radians += math.pi

bebop.move_relative(1, 0, 0, 0)
Lat_End = bebop.sensors.sensors_dict["GpsLocationChanged_latitude"]
Lon_End = bebop.sensors.sensors_dict["GpsLocationChanged_longitude"]

dlat = Lat_End - Lat_Start
dlon = Lon_End - Lon_Start
current_radians = math.atan(dlat/dlon)
if(dlon < 0):
    current_radians += math.pi

difference_degrees = math.degrees(loc_radians - current_radians)
bebop.move_relative(0,0,0,difference_degrees)

bebop.smart_sleep(5)
bebop.safe_land(10)

print("DONE - disconnecting")
bebop.disconnect()