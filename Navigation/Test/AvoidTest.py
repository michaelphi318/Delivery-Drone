from pyparrot.Bebop import Bebop
import sys, signal
from threading import Thread, Condition
import time
from math import radians, cos, sin, asin, atan, sqrt, pi


#---------------------------Threads----------------------------
# Threads via inheritance
# GPS: Drone will take new GPS constantly
# Arrive: Drone will use this thread to navigate to location
# Avoidance: Drone will use this thread to avoid obstacles

class GPS(Thread):
    def __init__(self):
        super().__inint__()
        self.coords = [[0.0, 0.0, 0.0]] * 3
        self.latitude_destination = 39.96147141121459
        self.longitude_destination = -75.18766440922718

    def distanceGPS(self, lat1, lon1, lat2, lon2):
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

    def diffRadians(self, lat, lon, preLat, preLon):
        loc_radians = atan((self.latitude_destination - lat) / (self.longitude_destination - lon))

        if self.longitude_destination - lon < 0:
            loc_radians += pi
            
        dlat = lat - preLat
        dlon = lon - preLon
        current_radians = atan(dlat / dlon)

        if (dlon < 0):
            current_radians += pi
            
        # diff_radians = current_radians - loc_radians
        diff_radians = loc_radians - current_radians

        return diff_radians

    def run(self):
        while True:
            lat = bebop.sensors.sensors_dict["GpsLocationChanged_latitude"]
            lon = bebop.sensors.sensors_dict["GpsLocationChanged_longitude"]
            alt = bebop.sensors.sensors_dict["GpsLocationChanged_altitude"]
        
            if(self.coords[2][0] != lat and lat != 500):
                self.coords.append([lat, lon, alt])
                self.coords.pop(0)

class Arrive(Thread):
    def __init__(self):
        super().__init__()
        # python program exits when only daemon threads are left
        # self.daemon = True
        self.stopped = True
        self.condition = Condition()
        self.gps = GPS()

    def arrive(self):
        d = 1000
        p = 100
        v = 2

        lat = 0
        lon = 0

        bebop.move_relative(0, 0, -1, 0)
        
        # bebop.smart_sleep(0.2)

        while(self.gps.coords[0][0] == 0):
            continue

        lat = (self.gps.coords[0][0] + self.gps.coords[1][0] + self.gps.coords[2][0]) / 3
        lon = (self.gps.coords[0][1] + self.gps.coords[1][1] + self.gps.coords[2][1]) / 3
        
        loc_radians = atan((self.gps.latitude_destination - lat) / (self.gps.longitude_destination - lon))
        
        if((self.gps.longitude_destination - lon) < 0):
            loc_radians += pi
        
        prevLat = lat
        prevLon = lon
        
        print("Going foward\n")
        # bebop.fly_direct(roll=0, pitch=75, yaw=0, vertical_movement=0, duration=0.25)
        bebop.move_relative(2, 0, 0, 0)
        # bebop.smart_sleep(1)

        
        while((self.gps.coords[0][0] + self.gps.coords[1][0] + self.gps.coords[2][0]) / 3 == lat):
            continue

        lat = (self.gps.coords[0][0] + self.gps.coords[1][0] + self.gps.coords[2][0]) / 3
        lon = (self.gps.coords[0][1] + self.gps.coords[1][1] + self.gps.coords[2][1]) / 3

        d = self.gps.distanceGPS(lat, lon, self.gps.latitude_destination, self.gps.longitude_destination)
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
            
            diff_radians = self.gps.diffRadians(lat, lon, prevLat, prevLon)

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

            while((self.gps.coords[0][0] + self.gps.coords[1][0] + self.gps.coords[2][0]) / 3 == lat):
                print("Break")
                bebop.move_relative(v, 0, 0, 0)

            lat = (self.gps.coords[0][0] + self.gps.coords[1][0] + self.gps.coords[2][0]) / 3
            lon = (self.gps.coords[0][1] + self.gps.coords[1][1] + self.gps.coords[2][1]) / 3

            d = self.gps.distanceGPS(lat, lon, self.gps.latitude_destination, self.gps.longitude_destination)
            print("Distance to destination: " + str(d) + " m\n")
        # bebop.safe_land(5)
        # bebop.disconnect()
        # sys.exit(0)
    
    def run(self):
        self.resume()

        while True:
            with self.condition:
                if self.stopped:
                    self.condition.wait()
            # print("Flying")
            # self.arrive()
            bebop.move_relative(10, 0, 0, 0)
    
    def pause(self):
        self.stopped = True

    def resume(self):
        with self.condition:
            self.stopped = False
            self.condition.notify()

class Avoidance(Thread):
    def __init__(self):
        super().__init__()
        # python program exits when only daemon threads are left
        # self.daemon = True
        self.stopped = True
        self.condition = Condition()

    def run(self):
        self.resume()

        while True:
            with self.condition:
                if self.stopped:
                    self.condition.wait()
            # print("Stop Flying")
            bebop.cancel_move_relative()
    
    def pause(self):
        self.stopped = True

    def resume(self):
        with self.condition:
            self.stopped = False
            self.condition.notify()
#--------------------------------------------------------------


#------------------------Test case-----------------------------
def test():
    #---------------------Declare threads----------------------
    threads = []
    t1 = Arrive()
    t2 = Avoidance()
    threads.append(t1)
    threads.append(t2)
    #----------------------------------------------------------

    #---------------------Execute threads----------------------
    # for thread in threads:
    #     thread.start()
    t1.start()
    t2.start()
    
    # imediately pause Avoidance thread
    t1.resume()
    t2.pause()

    # Test case
    for i in range(3):
        print("Iteration %d" % (i + 1))
        t1.resume()
        t2.pause()
        time.sleep(0.5)
        t1.pause()
        t2.resume()
        time.sleep(0.5)
        # t1.resume()
        # t2.pause()
        print()
    #----------------------------------------------------------

    #--------------Disconnect and Land the drone---------------
    bebop.safe_land(5)
    bebop.disconnect()
    sys.exit(0)
    #----------------------------------------------------------

#--------------------------------------------------------------


#-------------------------Main---------------------------------
if __name__ == "__main__":

    #---------------------Connect and Fly----------------------
    bebop = Bebop()
    print("Connecting to the drone\n")
    success = bebop.connect(10)
    print(success)

    # if not success:
    #     print("Connection failed\n")
    #     sys.exit(1)
        
    # print("Sleeping")
    bebop.smart_sleep(3)

    # take off
    bebop.safe_takeoff(10)
    #---------------------------------------------------------

    #------------------------Test-----------------------------
    try:
        test()
    except:
        bebop.safe_land(5)
        bebop.disconnect()
    finally:
        sys.exit(1)
    #---------------------------------------------------------

#-------------------------------------------------------------


#-----------------------Old shit------------------------------
# def t1():
#     bebop.move_relative(15, 0, 0, 0)
#     # bebop.smart_sleep(1)

# def t2():
#     time.sleep(0.3)
#     # bebop.smart_sleep(1)
#     bebop.cancel_move_relative()
    

# if __name__ == "__main__":
#     bebop = Bebop()
#     trigger = False
    
#     print("Connecting to the drone\n")
#     success = bebop.connect(10)
#     print(success)

#     # if not success:
#     #     print("Connection failed\n")
#     #     sys.exit(1)
    
#     # print("Sleeping")
#     bebop.smart_sleep(3)

#     # take off
#     bebop.safe_takeoff(10)

#     # create threads
#     thread1 = Thread(target=t1, args=())
#     thread2 = Thread(target=t2, args=())

#     thread1.start()
#     thread2.start()

#     thread1.join()
#     thread2.join()

#     # bebop.move_relative(10, 0, 0, 0)
#     # bebop.smart_sleep(1)
#     # bebop.cancel_move_relative()
#     # bebop.smart_sleep(1)

#     bebop.safe_land(5)
#     bebop.disconnect()
#----------------------------------------------------------
