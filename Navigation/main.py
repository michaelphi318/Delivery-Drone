from pyparrot.Bebop import Bebop
from threading import Thread
from gps import *
from arrive import *
from avoidance import *
from logger import *
import sys, os, time, datetime, traceback


# class DroneController():
#     def __inint__(self):
#         self.lat, self.lon = self.readGPSFromFile()
#         self.bebop = Bebop()
#         self.arriveThread = Arrive(self.bebop, self.lat, self.lon)
#         self.avoidanceThread = Avoidance(self.bebop)
#         self.threads = [self.arriveThread, self.arriveThread.gps, self.avoidanceThread]

#     def readGPSFromFile(self):
#         data = []
#         fname = os.path.dirname(os.path.realpath(__file__)) + "/gps.txt"

#         with open(fname, "r") as f:
#             data = list(map(float, f.readlines()))

#         return data[0], data[1]

#     def droneConnect(self):
#         print("\nConnecting to the drone\n")
#         success = self.bebop.connect(5)

#         if not success:
#             print("Connection failed\n")
#             sys.exit(1)
            
#         self.bebop.smart_sleep(2)
    
#     def droneCalibrate(self):
#         start_time = time.time()
#         self.bebop.flat_trim(0)
#         end_time = time.time()
#         print("Flat trim finished after %.2f" % (end_time - start_time))

#     def droneTakeOff(self):
#         self.bebop.safe_takeoff(10)

#     def droneAutonomousControl(self):
#         try:
#             for thread in self.threads:
#                 if isinstance(thread, (Arrive, GPS, Avoidance)):
#                     thread.start()

#             for thread in self.threads:
#                 if isinstance(thread, (Arrive, GPS, Avoidance)):
#                     thread.terminate = True
#                     thread.join()
#                     print("Thread %s terminated" % (thread.__class__.__name__))

#             sys.exit(0)
#         except:
#             print("Error in Main thread\n")
#             traceback.print_exc()
#             print("\n\nEmergency land the drone")
#             bebop.safe_land(5)
#             bebop.disconnect()
#             os._exit(1)


def userInput():
    global stop

    while True:
        command = input().lower()

        #-----------------------------------
        # q = emergengy land
        # p = Arrive pause, Avoidance resume
        # r = Arrive resume, Avoidance pause
        # b = break the thread
        #-----------------------------------

        if command == "q":
            bebop.safe_land(10)
            print("Emergency landing protocol - disconnecting")
            bebop.disconnect()
            os._exit(1)
        elif command == "p":
            stop = True
        elif command == "r":
            stop = False
        elif command == "b":
            break
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
    arriveThread = Arrive(bebop, lat, lon)
    avoidanceThread = Avoidance(bebop)
    inputThread = Thread(target=userInput)
    threads = [arriveThread, arriveThread.gps, avoidanceThread]
    #----------------------------------------------------------

    try:
        for thread in threads:
            if isinstance(thread, (Arrive, GPS, Avoidance)):
                thread.start()
        
        inputThread.start()

        while arriveThread.distance > 0.25:
            if stop:
                arriveThread.pause()
                avoidanceThread.resume()
            else:
                arriveThread.resume()
                avoidanceThread.pause()
        
        print("While loop exited (main)")

        for thread in threads:
            if isinstance(thread, (Arrive, GPS, Avoidance)):
                thread.terminate = True
                thread.join()
                print("Thread %s terminated" % (thread.__class__.__name__))

        inputThread.join()
        sys.exit(0)
    except:
        print("Error in Main thread\n")
        traceback.print_exc()
        print("\n\nEmergency land the drone")
        bebop.safe_land(5)
        bebop.disconnect()
        os._exit(1)

# flat trim function
def calibrate():
    start_time = time.time()
    bebop.flat_trim(0)
    end_time = time.time()
    print("Flat trim finished after %.2f" % (end_time - start_time))

def connect():
    print("\nConnecting to the drone\n")
    success = bebop.connect(5)

    if not success:
        print("Connection failed\n")
        sys.exit(1)
        
    bebop.smart_sleep(2)
    calibrate()
    

if __name__ == "__main__":
    bebop = Bebop()
    stop = False    # test boolean
    path = os.path.dirname(os.path.realpath(__file__)) + "/log.txt"
    sys.stdout = Logger(path)
    sys.stderr = sys.stdout
    print(datetime.date.today().strftime("\n\n%d/%m/%Y"))
    print(datetime.datetime.now().strftime("%H:%M:%S"))

    connect()
    bebop.safe_takeoff(10)
    test()