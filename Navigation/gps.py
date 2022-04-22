from inspect import trace
from pyparrot.Bebop import Bebop
from threading import Thread
from math import radians, cos, sin, asin, atan, sqrt, pi
from logger import *
import sys, os, time, traceback


class GPS(Thread):
    def __init__(self, bebop, lat, lon):
        super().__init__()
        self.terminate = False
        if isinstance(bebop, Bebop):
            self.bebop = bebop
        self.coords = [[0.0, 0.0, 0.0] for i in range(3)] 
        self.latitude_destination = lat
        self.longitude_destination = lon

    def avgGPS(self):
        lat_sum = 0
        lon_sum = 0
        alt_sum = 0

        for i in range(len(self.coords)):
            lat_sum += self.coords[i][0]
            lon_sum += self.coords[i][1]
            alt_sum += self.coords[i][2]
        
        lat = lat_sum / len(self.coords)
        lon = lon_sum / len(self.coords)
        alt = alt_sum / len(self.coords)

        return lat, lon

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
        # Raius of earth in m
        r = 6371 * 1000
        
        # calculate the result
        d = c * r
        print("Distance to destination: %.2f m\n" % (d))

        return d

    def diffRadians(self, lat, lon, preLat, preLon):
        loc_radians = atan((self.latitude_destination - lat) / (self.longitude_destination - lon))

        if self.longitude_destination - lon < 0:
            loc_radians += pi
            
        dlat = lat - preLat
        dlon = lon - preLon
        current_radians = atan(dlat / dlon)

        if (dlon < 0):
            current_radians += pi
            
        diff_radians = loc_radians - current_radians

        return diff_radians

    def run(self):
        try:
            while True:
                if self.terminate:
                    break
                
                lat = self.bebop.sensors.sensors_dict["GpsLocationChanged_latitude"]
                lon = self.bebop.sensors.sensors_dict["GpsLocationChanged_longitude"]
                alt = self.bebop.sensors.sensors_dict["GpsLocationChanged_altitude"]
            
                if (self.coords[2][0] != lat):
                    self.coords.append([lat, lon, alt])
                    self.coords.pop(0)
        except:
            traceback.print_exc()
            print()
            # print("\nEmergency land the drone")
            self.bebop.safe_land(5)
            self.bebop.disconnect()
        finally:
            print("Error in GPS class")