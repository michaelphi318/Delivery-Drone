from pyparrot.Bebop import Bebop
from threading import Thread, Condition
from math import atan, pi
from gps import *


class Arrive(Thread):
    def __init__(self, bebop, lat, lon):
        super().__init__()
        if isinstance(bebop, Bebop):
            self.bebop = bebop
        self.stopped = True
        self.condition = Condition()
        self.gps = GPS(self.bebop, lat, lon)
    
    def run(self):
        def checkMove():
            for i in range(len(self.gps.coords)):
                if self.gps.coords[i][0] == 500:
                    self.bebop.loop_breaker = True
                    self.bebop.cancel_move_relative()
                    print("GPS is bad, switch to fly_direct")
                    print("Going foward\n")
                    self.bebop.fly_direct(roll=0, pitch=75, yaw=0, vertical_movement=0, duration=0.25)

        d = 1000
        p = 100
        v = 2
        lat = 0
        lon = 0

        self.resume()
        self.gps.start()

        #------------------------------------Fly the drone foward-----------------------------------------
        print("Fly up 1m\n")
        self.bebop.move_relative(0, 0, -1, 0)
        checkMove()
        
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
        
        print("Going forward to check for angle\n")
        self.bebop.move_relative(2, 0, 0, 0)
        checkMove()
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
                # checkMove()
            
            print("Going forward\n")
            #bebop.fly_direct(roll=0, pitch=p, yaw=0, vertical_movement=0, duration=0.5)
            self.bebop.move_relative(v, 0, 0, 0)
            checkMove()
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

        #--------------Disconnect and Land the drone---------------
        self.bebop.safe_land(5)
        self.bebop.disconnect()
        #----------------------------------------------------------
    
    def pause(self):
        self.stopped = True

    def resume(self):
        with self.condition:
            self.stopped = False
            self.condition.notify()