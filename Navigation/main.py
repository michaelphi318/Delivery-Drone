from pyparrot.Bebop import Bebop
import sys, os
from threading import Thread
from gps import *
from arrive import *
from avoidance import *
from logger import *

def userInput():
    global stop

    while True:
        command = input().lower()

        if command == "q":
            bebop.safe_land(10)
            print("Emergency landing protocol - disconnecting")
            bebop.disconnect()
            sys.exit(1)
        elif command == "p":
            stop = True


def test():
    #---------------------Declare------------------------------
    lat = 39.96093390559246
    lon = -75.18765920833292
    arrive = Arrive(bebop, lat, lon)
    avoidance = Avoidance(bebop)
    inputThread = Thread(target=userInput)
    #----------------------------------------------------------

    arrive.start()
    inputThread.start()
    avoidance.start()

    while arrive.is_alive:
        if stop:
            arrive.pause()
            avoidance.resume()
        else:
            arrive.resume()
            avoidance.pause()
    
    arrive.join()
    sys.exit(0)

def connect():
    print("Connecting to the drone\n")
    success = bebop.connect(5)

    if not success:
        print("Connection failed\n")
        sys.exit(1)
        
    bebop.smart_sleep(2)
    

if __name__ == "__main__":
    bebop = Bebop()
    stop = False    # test boolean
    path = os.path.dirname(os.path.realpath(__file__)) + "/log.txt"
    sys.stdout = Logger(path)

    connect()
    bebop.safe_takeoff(10)
    test()