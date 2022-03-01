from pyparrot.Bebop import Bebop
import sys, signal
from threading import Thread
import time
from math import radians, cos, sin, asin, atan, sqrt, pi


def t1():
    bebop.move_relative(10, 0, 0, 0)
    bebop.smart_sleep(1)

def t2():
    time.sleep(0.5)
    bebop.cancel_move_relative()
    bebop.smart_sleep(1)
    

if __name__ == "__main__":
    bebop = Bebop()
    
    print("Connecting to the drone\n")
    success = bebop.connect(10)
    print(success)

    # if not success:
    #     print("Connection failed\n")
    #     sys.exit(1)
    
    # print("Sleeping")
    bebop.smart_sleep(1)

    # take off
    bebop.safe_takeoff(10)
    bebop.smart_sleep(2)

    # create threads
    thread1 = Thread(target=t1)
    thread2 = Thread(target=t2)

    thread1.start()
    thread2.start()

    thread1.join()
    thread2.join()

    # bebop.move_relative(10, 0, 0, 0)
    # bebop.smart_sleep(1)
    # bebop.cancel_move_relative()
    # bebop.smart_sleep(1)

    bebop.safe_land(5)
    bebop.disconnect()

