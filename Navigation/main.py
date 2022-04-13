from pyparrot.Bebop import Bebop
import sys, signal
from threading import Thread, Condition
import time
from math import radians, cos, sin, asin, atan, sqrt, pi
from gps import *
from arrive import *
from avoidance import *

def exit():
    while True:
        user_input = input("Enter your command: ")
        if (user_input.lower() == "q"):
            bebop.safe_land(10)
            print("Emergency landing protocol - disconnecting")
            bebop.disconnect()
            sys.exit(1)

def test():
    #---------------------Declare------------------------------
    lat = 39.961346144444555
    lon = -75.18747012777759
    arrive = Arrive(bebop, lat, lon)
    avoidance = Avoidance(bebop)
    exitThread = Thread(target=exit)
    #----------------------------------------------------------

    #---------------------Execute threads----------------------
    arrive.gps.start()
    arrive.start()
    exitThread.start()
    # t2.start()
    
    arrive.gps.join()
    arrive.join()
    exitThread.join()
    # t2.join()
    
    # imediately pause Avoidance thread
    # t1.resume()
    # t2.pause()

    # Test case
    # for i in range(3):
        # print("Iteration %d" % (i + 1))
        # t1.resume()
        # t2.pause()
        # time.sleep(0.5)
        # t1.pause()
        # t2.resume()
        # time.sleep(0.5)
        # t1.resume()
        # t2.pause()
        # print()
    #----------------------------------------------------------

def connect():
    print("Connecting to the drone\n")
    success = bebop.connect(10)

    if not success:
        print("Connection failed\n")
        sys.exit(1)
        
    # print("Sleeping")
    bebop.smart_sleep(3)
    

if __name__ == "__main__":
    bebop = Bebop()

    connect()
    bebop.safe_takeoff(10)
    test()