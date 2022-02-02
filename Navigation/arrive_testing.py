from pyparrot.Bebop import Bebop
from math import radians, cos, sin, asin, atan, sqrt, pi
# pip install numpy
import numpy as np
import signal
import sys


LATITUDE_DESTINATION = 39.96166130276774
LONGTITUDE_DESTINATION = -75.18769108889548
#LATITUDE_ORIGIN = 0
#LONGTITUDE_ORIGIN = 0

def handler(signum, frame):
    bebop.safe_land(10)
    print("Safe land protocol - disconnecting")
    bebop.disconnect()
    sys.exit(1)

def distanceGPS(lat1, lon1, lat2, lon2):
    # convert from degree to radians
    #lat1 = radians(lat1)
    #lon1 = radians(lon1)
    #lat2 = radians(lat2)
    #lon2 = radians(lon2)

    # haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
 
    c = 2 * asin(sqrt(a))
    
    # Radius of earth in kilometers (6371). Use 3956 for miles
    #r = 6371
    # Raius of earth in m
    r = 6371 * 1000
      
    # calculate the result
    return (c * r)

def precisionGPS(bebop):
    lat_min = -2000
    lat_max = 2000
    lon_min = -2000
    lon_max = 2000
    alt_min = -2000
    alt_max = 2000
    
    for i in range(10):
        lat = bebop.sensors.sensors_dict["GpsLocationChanged_latitude"]
        lon = bebop.sensors.sensors_dict["GpsLocationChanged_longitude"]
        alt = bebop.sensors.sensors_dict["GpsLocationChanged_altitude"]
        
        if(lat_min > lat):
            lat_min = lat
        if(lat_max < lat):
            lat_max = lat
        if(lon_min > lon):
            lon_min = lon
        if(lon_max < lon):
            lon_max = lon
        if(alt_min > alt):
            alt_min = alt
        if(alt_max < alt):
            alt_max = alt

        lat_precision = (lat_max - lat_min) * 364000
        lon_precision = (lon_max - lon_min) * 288200
        alt_precision = (alt_max - alt_min) * 3.28084
        #print("Latitude Precision: " + str(lat_precision) + " feet")
        #print("Longitdue Precision: " + str(lon_precision) + " feet")
        #print("Altitude Precision: " + str(alt_precision) + " feet")

        return lat_precision, lon_precision

def avgGPS(bebop):
    lat_sum = 0
    lon_sum = 0
    alt_sum = 0

    for i in range(10):
        lat = bebop.sensors.sensors_dict["GpsLocationChanged_latitude"]
        lon = bebop.sensors.sensors_dict["GpsLocationChanged_longitude"]
        alt = bebop.sensors.sensors_dict["GpsLocationChanged_altitude"]
        lat_sum += lat
        lon_sum += lon
        alt_sum += alt 
        #bebop.smart_sleep(0.5)
    
    lat_avg = lat_sum / 10
    lon_avg = lon_sum / 10
    alt_avg = alt_sum / 10

    return lat_avg, lon_avg


if __name__ == "__main__":
    signal.signal(signal.SIGINT, handler)

    bebop = Bebop()
    print("Connecting")
    success = bebop.connect(10)
    print(success)

    if not success:
        print("FAILED")
        sys.exit(1)

    print("Sleeping")
    bebop.smart_sleep(2)
    
    print("Take off")
    bebop.safe_takeoff(5)
    bebop.move_relative(0, 0, -1, 0)
    print("Sleeping")
    bebop.smart_sleep(2)

    loc_raidans = atan(LATITUDE_DESTINATION / LONGTITUDE_DESTINATION)
    
    lat = bebop.sensors.sensors_dict["GpsLocationChanged_latitude"]
    lon = bebop.sensors.sensors_dict["GpsLocationChanged_longitude"]
    d = distanceGPS(lat, lon, LATITUDE_DESTINATION, LONGTITUDE_DESTINATION)

    for i in np.arange(0, d, 1.0):
        lat, lon = avgGPS(bebop)
        dlat = lat - LATITUDE_DESTINATION
        dlon = lon - LONGTITUDE_DESTINATION
        current_radians = atan(dlat / dlon)
        
        if (dlon < 0):
            current_radians += pi 
        
        diff_radians = loc_raidans - current_radians
        bebop.move_relative(1, 0, 0, -diff_radians)
    
    bebop.safe_land(5)
    print("DONE - Disconnecting")
    bebop.disconnect()
    sys.exit(0)

