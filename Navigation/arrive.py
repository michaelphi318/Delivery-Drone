from pyparrot.Bebop import Bebop
from threading import Thread, Condition
from math import atan, pi
from gps import GPS
import sys, os, time, traceback


class Arrive(Thread):
    def __init__(self, bebop, lat, lon):
        super().__init__()
        if isinstance(bebop, Bebop):
            self.bebop = bebop
        self.isPaused = True
        self.isTerminated = False
        self.condition = Condition()
        self.gps = GPS(self.bebop, lat, lon)
        self.distance = 1000.0
    
    def run(self):
        # def checkMove(v):
        #     for i in range(len(self.gps.coords)):
        #         if self.gps.coords[i][0] == 500:
        #             print("GPS is bad")
        #             print("Going foward\n")
        #             self.bebop.fly_direct(roll=0, pitch=75, yaw=0, vertical_movement=0, duration=0.25)
        #     self.bebop.move_relative(v, 0, 0, 0)

        # p = 100
        v = 2
        # lat = 0
        # lon = 0

        self.resume()

        try:
            #------------------------------------Fly the drone foward-----------------------------------------
            print("Fly up 2m\n")
            self.bebop.move_relative(0, 0, -2, 0)
            
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
            # checkMove(2)
            # bebop.smart_sleep(1)
            
            # while(self.gps.avgGPS() == lat):
            #     continue

            # lat = (self.gps.coords[0][0] + self.gps.coords[1][0] + self.gps.coords[2][0]) / 3
            # lon = (self.gps.coords[0][1] + self.gps.coords[1][1] + self.gps.coords[2][1]) / 3
            lat, lon = self.gps.avgGPS()

            self.distance = self.gps.distanceGPS(lat, lon, self.gps.latitude_destination, self.gps.longitude_destination)
            
            self.bebop.max_tilt(30)
            self.bebop.max_vertical_speed(5)
            self.bebop.max_rotation_speed(200)
            self.bebop.max_horizontal_speed(5)
            #-----------------------------------------------------------------------------------------------------

            #--------------------------------------Fly to destination---------------------------------------------
            # TODO
            # Fix lat and lon placement in the code
            # Adjust event lock
            while self.distance > 0.4:
                timeout = 0

                with self.condition:
                    if self.isPaused:
                        self.condition.wait()
                
                if self.distance > 10:
                    # p = 100
                    v = 8
                    timeout = 5
                elif self.distance > 5:
                    # p = 75
                    v = 4
                    timeout = 4
                elif self.distance <= 3 and self.distance > 1:
                    # p = 25
                    v = 2
                    timeout = 3
                elif self.distance < 1 and self.distance > 0.5:
                    # p = 10
                    v = 0.75
                    timeout = 2
                else:
                    # p = 5
                    v = 0.3875
                    timeout = 2
                
                diff_radians = self.gps.diffRadians(lat, lon, prevLat, prevLon)

                with self.condition:
                    if self.isPaused:
                        # self.condition.wait()
                        continue
                
                if abs(diff_radians) > 5 * pi / 180:
                    print("Rotating\n")
                    # self.bebop.smart_sleep(0.1)
                    self.bebop.move_relative(0, 0, 0, -diff_radians, timeout)
                    # checkMove()
                
                with self.condition:
                    if self.isPaused:
                        # self.condition.wait()
                        continue
                
                print("Going forward\n")
                #bebop.fly_direct(roll=0, pitch=p, yaw=0, vertical_movement=0, duration=0.5)
                self.bebop.move_relative(v, 0, 0, 0)
                # checkMove(v)
                # bebop.smart_sleep(0.5)
                
                prevLat = lat
                prevLon = lon

                # while((self.gps.coords[0][0] + self.gps.coords[1][0] + self.gps.coords[2][0]) / 3 == lat):
                #     print("Break")
                #     self.bebop.move_relative(v, 0, 0, 0)

                # lat = (self.gps.coords[0][0] + self.gps.coords[1][0] + self.gps.coords[2][0]) / 3
                # lon = (self.gps.coords[0][1] + self.gps.coords[1][1] + self.gps.coords[2][1]) / 3
                lat, lon = self.gps.avgGPS()

                self.distance = self.gps.distanceGPS(lat, lon, self.gps.latitude_destination, self.gps.longitude_destination)
            #--------------------------------------------------------------------------------------------------------

            #--------------Disconnect and Land the drone---------------
            print("Land the drone\n")
            self.bebop.safe_land(5)
            self.bebop.disconnect()
            # print("Arrive thread done\n")
            #----------------------------------------------------------
        except:
            print("Error in Arrive class\n")
            traceback.print_exc()
            print("\n\nEmergency land the drone")
            self.bebop.safe_land(5)
            self.bebop.disconnect()
            os._exit(1)
    
    def pause(self):
        self.isPaused = True

    def resume(self):
        with self.condition:
            self.isPaused = False
            self.condition.notify()