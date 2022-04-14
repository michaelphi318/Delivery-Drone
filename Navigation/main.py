from pyparrot.Bebop import Bebop
import sys, signal, os
from threading import Thread, Condition
import time
from math import radians, cos, sin, asin, atan, sqrt, pi
from gps import *
from arrive import *
from avoidance import *
from logger import *

def exit():
    while True:
        user_input = input()
        if (user_input.lower() == "q"):
            bebop.safe_land(10)
            print("Emergency landing protocol - disconnecting")
            bebop.disconnect()
            sys.exit(1)

def test():
    #---------------------Declare------------------------------
    lat = 39.96093390559246
    lon = -75.18765920833292
    arrive = Arrive(bebop, lat, lon)
    avoidance = Avoidance(bebop)
    exitThread = Thread(target=exit)
    #----------------------------------------------------------

    #---------------------Execute threads----------------------
    arrive.gps.start()
    arrive.start()
    exitThread.start()
    # avoidance.start()
    
    arrive.gps.join()
    arrive.join()
    exitThread.join()
    # avoidance.join()
    
    # imediately pause Avoidance thread
    # arrive.resume()
    # avoidance.pause()

    # Test case
    # arrive.resume()
    # avoidance.pause()
    # time.sleep(0.5)
    # arrive.pause()
    # avoidance.resume()
    # time.sleep(0.5)
    # arrive.resume()
    # avoidance.pause()
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
    path = os.path.dirname(os.path.realpath(__file__)) + "/log.txt"
    sys.stdout = Logger(path)
    
    connect()
    bebop.safe_takeoff(10)
    test()