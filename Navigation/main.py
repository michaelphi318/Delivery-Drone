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
    threads = []
    t1 = Arrive(bebop)
    t2 = Avoidance(bebop)
    threads.append(t1)
    threads.append(t2)
    #----------------------------------------------------------

    #---------------------Execute threads----------------------
    # for thread in threads:
    #     thread.start()
    t1.gps.start()
    t1.start()
    t1.join()
    t1.gps.join()
    # t2.start()
    
    # imediately pause Avoidance thread
    # t1.resume()
    # t2.pause()

    # Test case
    # for i in range(3):
    #     print("Iteration %d" % (i + 1))
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

    #--------------Disconnect and Land the drone---------------
    bebop.safe_land(5)
    bebop.disconnect()
    sys.exit(0)
    #----------------------------------------------------------

if __name__ == "__main__":
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

    test()

    # try:
    #     test()
    # except Exception as e:
    #     print(e)
    #     bebop.safe_land(5)
    #     bebop.disconnect()
    # finally:
    #     sys.exit(1)