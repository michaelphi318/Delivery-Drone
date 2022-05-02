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
    avoidanceThread : Avoidance(Thread)
        Thread object
        this thread will control how the drone avoid object
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
                resume avoidanceThread to stop the drone mid-fly
                pause the avoidanceThread to allow the drone to move again
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
        avoidanceThread : Avoidance(Thread)
            Thread object
            this thread will control how the drone avoid object
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
            resume avoidanceThread to stop the drone mid-fly
            pause the avoidanceThread to allow the drone to move again
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
                    # if isinstance(thread, (Arrive, GPS, Avoidance, NavigationSensor)):
                    thread.start()

                # Loop til distance is reached
                while self.arriveThread.distance > 0.25:
                    # object detected
                    if self.avoidanceThread.navi.isAvoidanceTriggered or self.avoidanceThread.navi.sensors[3] < self.avoidanceThread.navi.distanceThreshold:
                        case = self.avoidanceThread.navi.getAvoidanceCase()

                        print("Flying stop\n")
                        self.arriveThread.pause()
                        self.avoidanceThread.resume()

                        # For upper sensor
                        if self.avoidanceThread.navi.sensors[3] < self.avoidanceThread.navi.distanceThreshold:
                            self.avoidanceThread.pause()
                            self.avoidanceThread.moveUp()

                        # case in dictionary
                        elif case in self.cases.keys():
                            self.avoidanceThread.pause()

                            for command in self.cases.get(case):
                                command()
                        
                        # case not in dictionary, which should not happen
                        else:
                            raise ValueError("Avoidance case not in dict\n")
                    
                    # object not detected
                    else:
                        self.arriveThread.resume()
                        self.avoidanceThread.pause()
                
                # join all the threads
                for thread in self.threads:
                    # if isinstance(thread, (Arrive, GPS, Avoidance, NavigationSensor)):
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