from pyparrot.Bebop import Bebop
from pynput.keyboard import Key, KeyCode, Listener
from arrive import Arrive
from gps import GPS
from avoidance import Avoidance
from sensor import NavigationSensor
import sys, os, time, traceback


class DroneController():
    def __init__(self):
        self.lat, self.lon = self.readGPSFromFile()
        self.bebop = Bebop()
        self.arriveThread = Arrive(self.bebop, self.lat, self.lon)
        self.avoidanceThread = Avoidance(self.bebop)
        self.threads = [self.arriveThread, self.arriveThread.gps, self.avoidanceThread, self.avoidanceThread.navi]
        self.cases = {"000" : [self.avoidanceThread.moveDown], 
                        "001" : [self.avoidanceThread.turnRight, self.avoidanceThread.moveForward],
                        "010" : [self.avoidanceThread.turnLeft, self.avoidanceThread.moveForward],
                        "011" : [self.avoidanceThread.turnLeft, self.avoidanceThread.moveForward],
                        "100" : [self.avoidanceThread.turnRight, self.avoidanceThread.moveForward],
                        "101" : [self.avoidanceThread.turnRight, self.avoidanceThread.moveForward],
                        "110" : [self.avoidanceThread.turnLeft, self.avoidanceThread.moveForward],
                        "111" : [self.avoidanceThread.turnRight, self.avoidanceThread.moveForward]}

    def readGPSFromFile(self):
        data = []
        fname = os.path.dirname(os.path.realpath(__file__)) + "/gps.txt"

        with open(fname, "r") as f:
            data = list(map(float, f.readlines()))

        return data[0], data[1]

    def droneConnect(self):
        print("\nConnecting to the drone\n")
        success = self.bebop.connect(5)

        if not success:
            print("Connection failed\n")
            sys.exit(1)
            
        self.bebop.smart_sleep(2)
    
    def droneCalibrate(self):
        start_time = time.time()
        self.bebop.flat_trim(0)
        end_time = time.time()
        print("Calibrate finished after %.2f\n" % (end_time - start_time))

    def droneTakeOff(self):
        print("Take off")
        self.bebop.safe_takeoff(10)

    def droneAutonomousControl(self):
        try:
            for thread in self.threads:
                if isinstance(thread, (Arrive, GPS, Avoidance, NavigationSensor)):
                    thread.start()

            while self.arriveThread.distance > 0.25:
                if self.avoidanceThread.navi.isAvoidanceTriggered:
                    case = self.avoidanceThread.navi.getAvoidanceCase()

                    print("Flying stop\n")
                    self.arriveThread.pause()
                    self.avoidanceThread.resume()

                    # For upper sensor if equipped
                    # change (if case in self.cases.keys():) to (elif) if upper sensor is equipped
                    # if self.avoidanceThread.navi.sensors[3] < self.avoidanceThread.navi.distanceThreshold:
                    #     self.avoidanceThread.moveUp()

                    if case in self.cases.keys():
                        self.avoidanceThread.pause()

                        for command in self.cases.get(case):
                            command()
                    else:
                        raise ValueError("Avoidance case not in dict\n")
                else:
                    print("Flying resume\n")
                    self.arriveThread.resume()
                    self.avoidanceThread.pause()
            
            for thread in self.threads:
                if isinstance(thread, (Arrive, GPS, Avoidance, NavigationSensor)):
                    thread.isTerminated = True
                    thread.join()
                    print("Thread %s terminated" % (thread.__class__.__name__))

            sys.exit(0)
        except:
            print("Error in Main thread\n")
            traceback.print_exc()
            print("\n\nEmergency land the drone")
            self.bebop.safe_land(5)
            self.bebop.disconnect()
            os._exit(1)