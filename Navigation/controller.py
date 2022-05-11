from pyparrot.Bebop import Bebop
from pynput.keyboard import Key, KeyCode, Listener
from arrive import Arrive
from gps import GPS
from avoidance import Avoidance
from sensor import NavigationSensor
import sys, os, time, traceback


class DroneController():
    '''
    A class used to control the bebop drone

    Attribute
    -------------------------------------------------------------------------------------------------
    lat : double
        hold the latitude GPS data of the destination
    lon : double
        hold the longitude GPS data of the destination
    bebop : Bebop
        Bebop drone object
        the class will use method from this obj to manipulate the drone
    arriveThread : Arrive(Thread)
        Thread object
        this thread will control how the drone fly to the desination
        has GPS thread as one of its attribute
    avoidance : Avoidance()
        this object will control how the drone avoid object
        has NavigationSensor thread as one of its attribute
    threads : []
        a list to hold all of the threads (Arrive, GPS, Avoidance and NavigationSensor)
    cases : dictionary
        a dictionary that holds all of the avoidance cases as its keys
        and list of functions as the value for each key to navigate the drone
    --------------------------------------------------------------------------------------------------

    Method
    --------------------------------------------------------------------------------------------------
    readGPSFromFile() -> None
        read the GPS data from gps.txt, then assign the attribute lat and lon
    droneConnect() -> None
        connect to the bebop drone, exit if connection failed
    droneCalibrate() -> None
        calibrate the drone using flat_trim() method from Bebop
        pretty useless if you ask me, I included it just because reason
    droneTakeOff() -> None
        take off the drone using safe_takeoff() method from Bebop
    droneAutonomousControl() -> None
        fly the drone autonomously to the destination
        logic
            No obstacle ->
                fly normaly using arriveThread
            Obstacle ->
                pause arriveThread
                depends on the current case in the dictionary cases, move the drone based on its value
                no more obstacle -> arriveThread will resume again
    --------------------------------------------------------------------------------------------------
    '''
    
    def __init__(self):
        '''
        Attribute
        -------------------------------------------------------------------------------------------------
        lat : double
            hold the latitude GPS data of the destination
        lon : double
            hold the longitude GPS data of the destination
        bebop : Bebop
            Bebop drone object
            the class will use method from this obj to manipulate the drone
        arriveThread : Arrive(Thread)
            Thread object
            this thread will control how the drone fly to the desination
            has GPS thread as one of its attribute
        avoidance : Avoidance()
            this object will control how the drone avoid object
            has NavigationSensor thread as one of its attribute
        threads : []
            a list to hold all of the threads (Arrive, GPS, Avoidance and NavigationSensor)
        cases : dictionary
            a dictionary that holds all of the avoidance cases as its keys
            and list of functions as the value for each key to navigate the drone
        --------------------------------------------------------------------------------------------------
        '''

        self.lat, self.lon = self.readGPSFromFile()
        self.bebop = Bebop()
        self.arriveThread = Arrive(self.bebop, self.lat, self.lon)
        self.avoidance = Avoidance(self.bebop)
        self.threads = [self.avoidance.navi, self.arriveThread.gps, self.arriveThread]
        self.cases = {"000" : [self.avoidance.moveDown], 
                        "001" : [self.avoidance.turnRight, self.avoidance.moveForward],
                        "010" : [self.avoidance.turnLeft, self.avoidance.moveForward],
                        "011" : [self.avoidance.turnLeft, self.avoidance.moveForward],
                        "100" : [self.avoidance.turnRight, self.avoidance.moveForward],
                        "101" : [self.avoidance.turnRight, self.avoidance.moveForward],
                        "110" : [self.avoidance.turnLeft, self.avoidance.moveForward],
                        "111" : [self.avoidance.turnRight, self.avoidance.moveForward]}

    def readGPSFromFile(self):
        '''read the GPS data from gps.txt, then assign the attribute lat and lon'''
        
        data = []
        fname = os.path.dirname(os.path.realpath(__file__)) + "/gps.txt"

        with open(fname, "r") as f:
            data = list(map(float, f.readlines()))

        return data[0], data[1]

    def droneConnect(self):
        '''Connect to the bebop drone, exit if connection failed'''
        
        print("\nConnecting to the drone\n")
        success = self.bebop.connect(5)

        if not success:
            print("Connection failed")
            sys.exit(1)
            
        self.bebop.smart_sleep(2)
    
    def droneCalibrate(self):
        '''Calibrate the drone using flat_trim() method from Bebop

        Pretty useless if you ask me, I included it just because reasons
        '''
        
        start_time = time.time()
        self.bebop.flat_trim(0)
        end_time = time.time()
        print("Calibrate finished after %.2f\n" % (end_time - start_time))

    def droneTakeOff(self):
        '''Take off the drone using safe_takeoff() method from Bebop'''

        print("Take off")
        self.bebop.safe_takeoff(10)

    def droneAutonomousControl(self):
        '''Fly the drone autonomously to the destination
        
        Logic
        ----------------------------------------------------------------------------------------------
        No obstacle ->
            fly normaly using arriveThread
        Obstacle ->
            pause arriveThread
            depends on the current case in the dictionary cases, move the drone based on its value
            no more obstacle -> arriveThread will resume again
        ----------------------------------------------------------------------------------------------
        
        Exception
        ----------------------------------------------------------------------------------------------
        If run into any exception, land the drone and stop the whole program
        ----------------------------------------------------------------------------------------------
        '''
        
        def on_press(key):
            # print('{0} pressed'.format(key))
            pass

        def on_release(key):
            # print('{0} release'.format(key))
            if key == Key.esc:
                return False
            elif key == KeyCode.from_char("q"):
                self.bebop.safe_land(10)
                print("Emergeny landing protocol - disconnecting")
                self.bebop.disconnect()
                os._exit(1)

        try:
            with Listener(on_press=on_press, on_release=on_release) as listener:

                # Start all the threads
                for thread in self.threads:
                    thread.start()

                    # wait for sensors to be connected
                    # if isinstance(thread, NavigationSensor):
                    #     while not thread.isConnected:
                    #         continue

                # Loop til distance is reached
                while self.arriveThread.distance  > 0.25:
                
                    # if object detected
                    if self.avoidance.navi.sensors[3] < self.avoidance.navi.distanceThreshold or self.avoidance.navi.isAvoidanceTriggered:
                        # time.sleep(5)
                        # print(avoidanceThread.navi.sensors)
                        self.arriveThread.pause()
                        self.bebop.loop_breaker = True
                        self.bebop.loop_breaker = False
                        # self.bebop.sensors.RelativeMoveEnded = True
                        case = self.avoidance.navi.getAvoidanceCase()
                        # print("Case %s" % case)
                        
                        # if upper sensor and either front, left, right sees something
                        if self.avoidance.navi.sensors[3] < self.avoidance.navi.distanceThreshold and self.avoidance.navi.isAvoidanceTriggered:
                            if case in self.cases.keys():
                                for command in self.cases.get(case):
                                    command()
                            else:
                                raise ValueError("Avoidance case not in dictionary\n")
                        
                        # if only uppper sensor see something
                        elif self.avoidance.navi.sensors[3] < self.avoidance.navi.distanceThreshold and not self.avoidance.navi.isAvoidanceTriggered:
                            self.avoidance.moveDown()
                        
                        # if upper sensor doesn't see anything and either front, left, right see anything
                        elif self.avoidance.navi.sensors[3] > self.avoidance.navi.distanceThreshold and self.avoidance.navi.isAvoidanceTriggered:
                            self.avoidance.moveUp()
                    
                    # object not detected
                    else:
                        self.arriveThread.resume()
                        # self.bebop.loop_breaker = False

                # # Loop til distance is reached
                # while self.arriveThread.distance > 0.25:
                #     # object detected
                #     if self.avoidance.navi.isAvoidanceTriggered or self.avoidance.navi.sensors[3] < self.avoidance.navi.distanceThreshold:
                #         case = self.avoidance.navi.getAvoidanceCase()

                #         print("Flying stop\n")
                #         self.arriveThread.pause()
                #         self.bebop.loop_breaker = True
                #         time.sleep(0.1)
                #         self.bebop.loop_breaker = False

                #         # For upper sensor
                #         if self.avoidance.navi.sensors[3] < self.avoidance.navi.distanceThreshold:
                #             self.avoidance.moveUp()

                #         # case in dictionary
                #         elif case in self.cases.keys():
                #             for command in self.cases.get(case):
                #                 command()
                        
                #         # case not in dictionary, which should not happen
                #         else:
                #             raise ValueError("Avoidance case not in dict\n")
                    
                #     # object not detected
                #     else:
                #         self.arriveThread.resume()
            
                # join all the threads
                for thread in self.threads:
                    # if isinstance(thread, (Arrive, GPS, NavigationSensor)):
                    thread.isTerminated = True
                    thread.join()
                    print("Thread %s terminated" % (thread.__class__.__name__))

                listener.join()
                sys.exit(0)
        
        # Land the drone and quit the program if any exception occurs
        except:
            print("Error in Main thread\n")
            traceback.print_exc()
            print("\n\nEmergency land the drone")
            self.bebop.safe_land(5)
            self.bebop.disconnect()
            os._exit(1)