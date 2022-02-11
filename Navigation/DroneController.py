from tabnanny import verbose
from pyparrot.Bebop import Bebop
from threading import Thread
from math import radians, cos, sin, asin, atan, sqrt, pi
import sys
from adafruit_ble import BLERadio
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.services.nordic import UARTService

LATITUDE_DESTINATION = 39.96147750832829
LONGITUDE_DESTINATION = -75.187658591667
#LATITUDE_ORIGIN = 0
#LONGTITUDE_ORIGIN = 0

class DroneController:
    def __init__(self, drone):
        self.running = True
        self.drone = drone

    def terminate(self):
        self.running = False
    
    def connect(self, time):
        print("Connecting")
        success = self.drone.connect(time)
        print(success)
        
        return success

    def smart_sleep(self, time):
        print("Sleeping for " + str(time) + "seconds")
        self.drone.smart_sleep(time)

    def take_off(self, time):
        print("Take off")
        self.drone.safe_takeoff(time)
        self.drone.move_relative(0, 0, -1, 0)
        self.smart_sleep(time)

    def start(self, time):
        success = self.connect(time)
    
        # if not success:
        #     print("Failed")
        #     sys.exit(1)

        self.smart_sleep(time)
        self.take_off(time)
        

    def move_relative(self, dx, dy, dz, dradians):
        self.drone.move_relative(dx, dy, dz, dradians)

    def set_max_vertical_speed(self, speed):
        self.drone.set_max_vertical_speed(speed)

    def safe_land(self, time):
        print("Landing")
        self.drone.safe_land(time)
    
    def disconnect(self):
        print("Done - Disconnecting")
        self.drone.disconnect()

    # calculate distance between 2 GPS location
    def distance(self, lat1, lon1, lat2, lon2):
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
        print("Distance: " + str(c * r) + " m")
        return (c * r)

    # calculate diff_radians
    def diffRadians(self, lat, lon, preLat, preLon):
        loc_radians = atan((LATITUDE_DESTINATION - lat) / (LONGITUDE_DESTINATION - lon))

        if LONGITUDE_DESTINATION - lon < 0:
            loc_radians += pi
        
        dlat = lat - preLat
        dlon = lon - preLon
        current_radians = atan(dlat / dlon)

        if (dlon < 0):
            current_radians += pi
        
        diff_radians = current_radians - loc_radians

        return diff_radians

    # get the drone's current GPS
    def getGPS(self):
        lat = self.drone.sensors.sensors_dict["GpsLocationChanged_latitude"]
        lon = self.drone.sensors.sensors_dict["GpsLocationChanged_longitude"]
        alt = self.drone.sensors.sensors_dict["GpsLocationChanged_altitude"]

        return lat, lon, alt

    # calculte the drone's average current GPS in a specific sample size
    # using Thread
    def avgGPS(self, n):
        def handler(result, index):
            lat = self.drone.sensors.sensors_dict["GpsLocationChanged_latitude"]
            lon = self.drone.sensors.sensors_dict["GpsLocationChanged_longitude"]
            alt = self.drone.sensors.sensors_dict["GpsLocationChanged_altitude"]
            result[index] = [lat, lon, alt]

        lat_sum = 0
        lon_sum = 0
        alt_sum = 0
        result = [None] * n
        threads = [None] * n

        for i in range(n):
            threads[i] = Thread(target=handler, args=(result, i,))

        for thread in threads:
            thread.start()
        
        for thread in threads:
            thread.join()

        for i in range(len(result)):
            lat_sum += result[i][0]
            lon_sum += result[i][1]
            alt_sum += result[i][2]
        
        lat_avg = lat_sum / n
        lon_avg = lon_sum / n
        alt_avg = alt_sum / n

        return lat_avg, lon_avg
    
    def run(self):
        print("break1")
        while self.running:
            print("break2")
            if not self.connect(5):
                sys.exit(1)
            
            # Move forward
            # then check for angle
            # finally move to the destination
            lat, lon = self.avgGPS(10)
            loc_radians = atan((LATITUDE_DESTINATION - lat) / (LONGITUDE_DESTINATION - lon))

            if((LONGITUDE_DESTINATION - lon) < 0):
                loc_radians += pi

            preLat = lat
            preLon = lon

            self.move_relative(2, 0, 0, 0)
            self.set_max_vertical_speed(2.5)

            lat, lon = self.avgGPS(10)
            d = self.distance(lat, lon, LATITUDE_DESTINATION, LONGITUDE_DESTINATION)
            p = 100

            while d > 0.5:
                if d > 3:
                    p = 100
                elif d <= 3 and d > 1:
                    p = 50
                else:
                    p = 25
                
                diff_radians = self.diffRadians(3, lat, lon, preLat, preLon)
                
                self.move_relative(0, 0, 0, diff_radians)
                self.drone.fly_direct(roll=0, pitch=p, yaw=0, vertical_movement=0, duration=0.2)
                
                preLat = lat
                preLon = lon
                lat, lon = self.avgGPS(3)
                d = self.distance(lat, lon, LATITUDE_DESTINATION, LONGITUDE_DESTINATION)
            
            self.terminate()
        
        self.safe_land(5)
        self.disconnect()


# def task(result, index):
#     result[index] = index

# def test():
#     threads = [None] * 10
#     result = [None] * 10

#     for i in range(10):
#         threads[i] = Thread(target=task, args=(result, i,))
    
#     for thread in threads:
#         thread.start()
    
#     for thread in threads:
#         thread.join()

#     print(result)

# test()