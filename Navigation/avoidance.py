from pyparrot.Bebop import Bebop
from threading import Thread, Condition
from sensor import *
import sys, os, time, traceback


class Avoidance(Thread):
    def __init__(self, bebop):
        super().__init__()
        if isinstance(bebop, Bebop):
            self.bebop = bebop
        self.isPaused = True
        self.isTerminated = False
        self.condition = Condition()
        self.navi = NavigationSensor(self.bebop)

    def turnRight(self):
        print("Turn right")
        # TODO
    
    def turnLeft(self):
        print("Turn left")
        # TODO

    def moveForward(self):
        print("Move forward")
        # TODO

    def moveUp(self):
        print("Move up")
        # TODO
    
    def moveDown(self):
        print("Move down")
        # TODO

    def run(self):
        try:
            self.bebop.loop_breaker = True

            while not self.isTerminated:
                with self.condition:
                    if self.isPaused:
                        self.condition.wait()
                
                self.bebop.cancel_move_relative()
            
            print("Avoidance thread done\n")
        except:
            print("Error in Avoidance class\n")
            traceback.print_exc()
            print("\n\nEmergency land the drone")
            self.bebop.safe_land(5)
            self.bebop.disconnect()
            os._exit(1)
    
    def pause(self):
        self.isPaused = True

    def resume(self):
        with self.condition:
            self.isPaused = False
            self.condition.notify()