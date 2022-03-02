from pyparrot.Bebop import Bebop
import sys, signal
from threading import Thread
from statistics import mean
from math import radians, cos, sin, asin, atan, sqrt, pi

LATITUDE_DESTINATION = 39.96147141121459
LONGITUDE_DESTINATION = -75.18766440922718

def handler(signum, frame):
    bebop.safe_land(10)
    print("Emergency landing protocol - disconnecting")
    bebop.disconnect()
    sys.exit(1)

def distanceGPS(lat1, lon1, lat2, lon2):
    # convert from degree to radians
    lat1 = radians(lat1)
    lon1 = radians(lon1)
    lat2 = radians(lat2)
    lon2 = radians(lon2)

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

def t1(list):
    while True:
        lat = bebop.sensors.sensors_dict["GpsLocationChanged_latitude"]
        lon = bebop.sensors.sensors_dict["GpsLocationChanged_longitude"]
        alt = bebop.sensors.sensors_dict["GpsLocationChanged_altitude"]
        #bebop.smart_sleep(0.1)
        if(list[2][0] != lat and lat != 500):
            list.append([lat, lon, alt])
            list.pop(0)

        # lat_avg = (list[0][0] + list[1][0] + list[2][0]) / 3
        # lon_avg = (list[0][1] + list[1][1] + list[2][1]) / 3
        # alt_avg = (list[0][2] + list[1][2] + list[2][2]) / 3

        # print("Lat: " + str(lat_avg))
        # print("Lon: " + str(lon_avg))
        # print("Alt: " + str(alt_avg))

def t2(list):
    d = 1000
    p = 100
    v = 2

    lat = 0
    lon = 0


    bebop.move_relative(0, 0, -1, 0)
    
    # bebop.smart_sleep(0.2)

    while(list[0][0] == 0):
        continue

    lat = (list[0][0] + list[1][0] + list[2][0]) / 3
    lon = (list[0][1] + list[1][1] + list[2][1]) / 3
    
    loc_radians = atan((LATITUDE_DESTINATION - lat) / (LONGITUDE_DESTINATION - lon))
    
    if((LONGITUDE_DESTINATION - lon) < 0):
        loc_radians += pi
    
    prevLat = lat
    prevLon = lon
    
    print("Going foward\n")
    # bebop.fly_direct(roll=0, pitch=75, yaw=0, vertical_movement=0, duration=0.25)
    bebop.move_relative(2, 0, 0, 0)
    # bebop.smart_sleep(1)

    
    while((list[0][0] + list[1][0] + list[2][0]) / 3 == lat):
        continue

    lat = (list[0][0] + list[1][0] + list[2][0]) / 3
    lon = (list[0][1] + list[1][1] + list[2][1]) / 3

    d = distanceGPS(lat, lon, LATITUDE_DESTINATION, LONGITUDE_DESTINATION)
    print("Distance to destination: " + str(d) + " m\n")

    bebop.max_tilt(30)
    print("break2")
    bebop.max_vertical_speed(5)
    print("break3")
    bebop.max_rotation_speed(200)
    bebop.max_horizontal_speed(5)

    while(d > 0.25):
        for e in list:
            print(e)
        print()

        if d > 10:
            p = 100
            v = 8
        elif d > 5:
            p = 75
            v = 4
        elif d <= 3 and d > 1:
            p = 25
            v = 1.5
        elif d < 1 and d > 0.5:
            p = 10
            v = 0.75
        else:
            p = 5
            v = 0.3875
        
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

        if abs(diff_radians) > 5 * pi / 180:
            print("Rotating\n")
            bebop.smart_sleep(0.1)
            bebop.move_relative(0, 0, 0, -diff_radians)
        
        print("Going forward\n")
        #bebop.fly_direct(roll=0, pitch=p, yaw=0, vertical_movement=0, duration=0.5)
        bebop.move_relative(v, 0, 0, 0)
        # bebop.smart_sleep(0.5)
        
        prevLat = lat
        prevLon = lon

        while((list[0][0] + list[1][0] + list[2][0]) / 3 == lat):
            print("Break")
            bebop.move_relative(v, 0, 0, 0)

        lat = (list[0][0] + list[1][0] + list[2][0]) / 3
        lon = (list[0][1] + list[1][1] + list[2][1]) / 3

        d = distanceGPS(lat, lon, LATITUDE_DESTINATION, LONGITUDE_DESTINATION)
        print("Distance to destination: " + str(d) + " m\n")
    bebop.safe_land(5)
    bebop.disconnect()
    sys.exit(0)


def t3():
    while True:
        input = input("Enter your command: ")
        if (input.lower() == "q"):
            bebop.safe_land(10)
            print("Emergency landing protocol - disconnecting")
            bebop.disconnect()
            sys.exit(1)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, handler)

    bebop = Bebop()
    gpsList = [[0, 0, 0]] * 3
    
    print("Connecting to the drone\n")
    success = bebop.connect(10)
    print(success)

    if not success:
        print("Connection failed\n")
        sys.exit(1)
    
    # print("Sleeping")
    bebop.smart_sleep(1)

    bebop.safe_takeoff(10)
    bebop.smart_sleep(2)

    t1 = Thread(target=t1, args=(gpsList,))
    t2 = Thread(target=t2, args=(gpsList,))

    t1.start()
    t2.start()

    t1.join()
    t2.join()

    bebop.safe_land(5)
    bebop.disconnect()
    