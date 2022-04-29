from pyparrot.Bebop import Bebop
from threading import Thread, Condition
from math import pi
from sensor import NavigationSensor
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
        while self.navi.isAvoidanceTriggered:
            print("Turn right 10 degrees")
            self.bebop.move_relative(0, 0, 0, 10 * pi / 180)
            time.sleep(0.1)
        
        time.sleep(5)
        
        if self.navi.isAvoidanceTriggered:
            self.turnRight()
    
    def turnLeft(self):
        while self.navi.isAvoidanceTriggered:
            print("Turn left 10 degrees")
            self.bebop.move_relative(0, 0, 0, -10 * pi / 180)
            time.sleep(0.1)
        
        time.sleep(5)

        if self.navi.isAvoidanceTriggered:
            self.turnLeft()

    def moveForward(self):
        if self.navi.isAvoidanceTriggered:
            print("Not clear to move forward")
        else:
            self.bebop.move_relative(1, 0, 0, 0)

    def moveUp(self):
        while self.navi.isAvoidanceTriggered:
            print("Move up")
            self.bebop.move_relative(0, 0, -1, 0)
    
    def moveDown(self):
        while self.navi.isAvoidanceTriggered:
            print("Move down")
            self.bebop.move_relative(0, 0, 0.5, 0)

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