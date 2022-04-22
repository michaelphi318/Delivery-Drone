from pyparrot.Bebop import Bebop
from threading import Thread
from gps import *
from arrive import *
from avoidance import *
from logger import *
import sys, os, time, datetime, traceback


def userInput():
    global stop
    global terminate

    while True:
        if terminate:
            break

        command = input().lower()

        if command == "q":
            bebop.safe_land(10)
            print("Emergency landing protocol - disconnecting")
            bebop.disconnect()
            os._exit(1)
        elif command == "p":
            stop = True
        elif command == "r":
            stop = False
        else:
            continue

def readGPSFromFile():
    data = []
    fname = os.path.dirname(os.path.realpath(__file__)) + "/gps.txt"

    with open(fname, "r") as f:
        data = list(map(float, f.readlines()))

    return data[0], data[1]

def test():
    #---------------------Declare------------------------------
    lat, lon = readGPSFromFile()
    arrive = Arrive(bebop, lat, lon)
    avoidance = Avoidance(bebop)
    inputThread = Thread(target=userInput)
    threads = [arrive, arrive.gps, avoidance, inputThread]
    #----------------------------------------------------------

    try:
        for thread in threads:
            thread.start()

        while arrive.distance > 0.25:
            if stop:
                arrive.pause()
                avoidance.resume()
            else:
                arrive.resume()
                avoidance.pause()
        
        for thread in threads:
            thread.terminate = True
            thread.join()
            print("Thread terminated")

            sys.exit(0)
    except:
        traceback.print_exc()
        print("\nEmergency land the drone")
        bebop.safe_land(5)
        bebop.disconnect()
        sys.exit(1)

def calibrate():
    # flat trim 
    start_time = time.time()
    bebop.flat_trim(0)
    end_time = time.time()
    print("Flat trim finished after %.2f" % (end_time - start_time))

def connect():
    print("\nConnecting to the drone\n")
    success = bebop.connect(5)

    # if not success:
    #     print("Connection failed\n")
    #     sys.exit(1)
        
    bebop.smart_sleep(2)
    calibrate()
    

if __name__ == "__main__":
    bebop = Bebop()
    stop = False    # test boolean
    terminate = False  # test boolean
    path = os.path.dirname(os.path.realpath(__file__)) + "/log.txt"
    sys.stdout = Logger(path)
    sys.stderr = sys.stdout
    print("\n\n")
    print(datetime.date.today().strftime("%d/%m/%Y"))
    print(datetime.datetime.now().strftime("%H:%M:%S"))

    connect()
    bebop.safe_takeoff(10)
    test()