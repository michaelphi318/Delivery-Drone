from pyparrot.Bebop import Bebop
from math import radians, cos, sin, asin, atan, sqrt, pi
import signal
import sys


LATITUDE_DESTINATION = 39.9609891500046
LONGITUDE_DESTINATION = -75.18765755833356
#LATITUDE_ORIGIN = 0
#LONGTITUDE_ORIGIN = 0

def handler(signum, frame):
    bebop.safe_land(10)
    print("Emergency landing protocol - disconnecting")
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
    r = 6371 * 10
      
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

def diffRadians(lat, lon, preLat, preLon):
    loc_radians = atan((LATITUDE_DESTINATION - lat) / (LONGITUDE_DESTINATION - lon))

    if LONGITUDE_DESTINATION - lon < 0:
        loc_radians += pi
        
    dlat = lat - preLat
    dlon = lon - preLon
    current_radians = atan(dlat / dlon)

    if (dlon < 0):
        current_radians += pi
        
    # diff_radians = current_radians - loc_radians
    diff_radians = loc_radians - current_radians

    return diff_radians

def avgGPS(bebop, n):
    lat_sum = 0
    lon_sum = 0
    alt_sum = 0

    for i in range(n):
        lat = bebop.sensors.sensors_dict["GpsLocationChanged_latitude"]
        lon = bebop.sensors.sensors_dict["GpsLocationChanged_longitude"]
        alt = bebop.sensors.sensors_dict["GpsLocationChanged_altitude"]
        lat_sum += lat
        lon_sum += lon
        alt_sum += alt 
        bebop.smart_sleep(0.1)
    
    lat_avg = lat_sum / n
    lon_avg = lon_sum / n
    alt_avg = alt_sum / n

    return lat_avg, lon_avg

if __name__ == "__main__":
    signal.signal(signal.SIGINT, handler)

    bebop = Bebop()
    
    print("Connecting to the drone\n")
    success = bebop.connect(2)
    print(success)

    if not success:
        print("Connection failed\n")
        sys.exit(1)
    
    # print("Sleeping")
    bebop.smart_sleep(1)

    # set bebop current speed for fly_direct
    bebop.set_max_tilt(30)
    bebop.set_max_vertical_speed(2.5)
    
    print("Take off\n")
    bebop.safe_takeoff(1)

    bebop.fly_direct(roll=0, pitch=0, yaw=0, vertical_movement=100, duration=0.5)
    # bebop.move_relative(0, 0, -1, 0)
    
    # print("Sleeping")
    bebop.smart_sleep(1)
    
    lat, lon = avgGPS(bebop, 10)
    loc_radians = atan((LATITUDE_DESTINATION - lat) / (LONGITUDE_DESTINATION - lon))
    
    if((LONGITUDE_DESTINATION - lon) < 0):
        loc_radians += pi
    
    prevLat = lat
    prevLon = lon
    
    print("Going foward\n")
    bebop.fly_direct(roll=0, pitch=75, yaw=0, vertical_movement=0, duration=0.25)
    bebop.smart_sleep(1)
    # bebop.move_relative(2, 0, 0, 0)
    
    d = distanceGPS(lat, lon, LATITUDE_DESTINATION, LONGITUDE_DESTINATION)
    print("Distance to destination: " + str(d) + " m\n")
    
    # Repetitive part, check later when testing
    # lat, lon = avgGPS(bebop, 10)
    # loc_radians = atan((LATITUDE_DESTINATION - lat) / (LONGITUDE_DESTINATION - lon))
    # if((LONGITUDE_DESTINATION - lon) < 0):
    #     loc_radians += pi

    # dlat = lat - prevLat
    # dlon = lon - prevLon
    # current_radians = atan(dlat / dlon)
    
    p = 100
    v = 2

    while(d > 0.5):
        if d > 3:
            p = 75
            v = 2
        elif d <= 3 and d > 1:
            p = 50
            v = 1
        elif d < 1 and d > 0.5:
            p = 25
            v = 0.5
        else:
            p = 10
            v = 0.5
        
        lat, lon = avgGPS(bebop, 3)
        diff_radians = diffRadians(lat, lon, prevLat, prevLon)
        # loc_radians = atan((LATITUDE_DESTINATION - lat) / (LONGITUDE_DESTINATION - lon))
        
        # if((LONGITUDE_DESTINATION - lon) < 0):
        #     loc_radians += pi
        
        # dlat = lat - prevLat
        # dlon = lon - prevLon
        # current_radians = atan(dlat / dlon)
        
        # if (dlon < 0):
        #     current_radians += pi 
        
        # diff_radians = loc_radians - current_radians

        print("Rotating\n")
        bebop.move_relative(0, 0, 0, -diff_radians)
        
        print("Going forward\n")
        bebop.fly_direct(roll=0, pitch=p, yaw=0, vertical_movement=0, duration=0.25)
        bebop.smart_sleep(0.5)
        # bebop.move_relative(v, 0, 0, 0)
        
        prevLat = lat
        prevLon = lon
        lat, lon = avgGPS(bebop, 3)
        d = distanceGPS(lat, lon, LATITUDE_DESTINATION, LONGITUDE_DESTINATION)
        print("Distance to destination: " + str(d) + " m\n")

    print("\nPrepare for Landing\n")
    bebop.safe_land(2)
    print("DONE - Disconnecting")
    bebop.disconnect()
    sys.exit(0)
