from pyparrot.Bebop import Bebop
import sys, signal
from threading import Thread, Condition
import time
from math import radians, cos, sin, asin, atan, sqrt, pi
from gps import *
from arrive import *
from avoidance import *


def test():
    #---------------------Declare threads----------------------
    t1 = Arrive(bebop)
    t2 = Avoidance(bebop)
    #----------------------------------------------------------

    #---------------------Execute threads----------------------
    t1.gps.start()
    t1.start()
    # t2.start()
    
    t1.gps.join()
    t1.join()
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

    # Connect
    connect()

    # Take off
    bebop.safe_takeoff(10)
    
    # Fly
    test()