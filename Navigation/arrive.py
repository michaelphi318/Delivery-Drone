from pyparrot.Bebop import Bebop
import sys, signal
from threading import Thread, Condition
import time
from math import radians, cos, sin, asin, atan, sqrt, pi
from gps import *


class Arrive(Thread):
    def __init__(self, bebop):
        super().__init__()
        self.bebop = bebop
        # python program exits when only daemon threads are left
        # self.daemon = True
        self.stopped = True
        self.condition = Condition()
        self.gps = GPS(self.bebop)
    
    def run(self):
        self.resume()

        d = 1000
        p = 100
        v = 2
        lat = 0
        lon = 0

        #------------------------------------Fly the drone foward-----------------------------------------
        self.bebop.move_relative(0, 0, -1, 0)
        
        # bebop.smart_sleep(0.2)

        while self.gps.coords[0][0] == 0.0:
            continue

        # lat = (self.gps.coords[0][0] + self.gps.coords[1][0] + self.gps.coords[2][0]) / 3
        # lon = (self.gps.coords[0][1] + self.gps.coords[1][1] + self.gps.coords[2][1]) / 3
        lat, lon = self.gps.avgGPS()
        
        loc_radians = atan((self.gps.latitude_destination - lat) / (self.gps.longitude_destination - lon))
        
        if ((self.gps.longitude_destination - lon) < 0):
            loc_radians += pi
        
        prevLat = lat
        prevLon = lon
        
        print("Going foward\n")
        # bebop.fly_direct(roll=0, pitch=75, yaw=0, vertical_movement=0, duration=0.25)
        self.bebop.move_relative(2, 0, 0, 0)
        # bebop.smart_sleep(1)
        
        while(self.gps.avgGPS() == lat):
            continue

        # lat = (self.gps.coords[0][0] + self.gps.coords[1][0] + self.gps.coords[2][0]) / 3
        # lon = (self.gps.coords[0][1] + self.gps.coords[1][1] + self.gps.coords[2][1]) / 3
        lat, lon = self.gps.avgGPS()

        d = self.gps.distanceGPS(lat, lon, self.gps.latitude_destination, self.gps.longitude_destination)
        
        self.bebop.max_tilt(30)
        self.bebop.max_vertical_speed(5)
        self.bebop.max_rotation_speed(200)
        self.bebop.max_horizontal_speed(5)
        #-----------------------------------------------------------------------------------------------------

        #--------------------------------------Fly to destination---------------------------------------------
        while(d > 0.25):
            with self.condition:
                if self.stopped:
                    self.condition.wait()

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

            if abs(diff_radians) > 5 * pi / 180:
                print("Rotating\n")
                self.bebop.smart_sleep(0.1)
                self.bebop.move_relative(0, 0, 0, -diff_radians)
            
            print("Going forward\n")
            #bebop.fly_direct(roll=0, pitch=p, yaw=0, vertical_movement=0, duration=0.5)
            self.bebop.move_relative(v, 0, 0, 0)
            # bebop.smart_sleep(0.5)
            
            prevLat = lat
            prevLon = lon

            # while((self.gps.coords[0][0] + self.gps.coords[1][0] + self.gps.coords[2][0]) / 3 == lat):
            #     print("Break")
            #     self.bebop.move_relative(v, 0, 0, 0)

            # lat = (self.gps.coords[0][0] + self.gps.coords[1][0] + self.gps.coords[2][0]) / 3
            # lon = (self.gps.coords[0][1] + self.gps.coords[1][1] + self.gps.coords[2][1]) / 3
            lat, lon = self.gps.avgGPS()

            d = self.gps.distanceGPS(lat, lon, self.gps.latitude_destination, self.gps.longitude_destination)
        #--------------------------------------------------------------------------------------------------------

        # self.arrive()
        # print("Flying")
        # bebop.move_relative(10, 0, 0, 0)

        #--------------Disconnect and Land the drone---------------
        self.bebop.safe_land(5)
        self.bebop.disconnect()
        sys.exit(0)
        #----------------------------------------------------------
    
    def pause(self):
        self.stopped = True

    def resume(self):
        with self.condition:
            self.stopped = False
            self.condition.notify()