from pyparrot.Bebop import Bebop
from threading import Thread, Condition
import sys, os, time, traceback


class Avoidance(Thread):
    def __init__(self, bebop):
        super().__init__()
        if isinstance(bebop, Bebop):
            self.bebop = bebop
        self.stopped = True
        self.terminate = False
        self.condition = Condition()

    def turnRight(self):
        print("Turn right")
    
    def turnLeft(self):
        print("Turn left")

    def moveForward(self):
        print("Move forward")

    def moveUP(self):
        print("Move up")

    def run(self):
        try:
            while True:
                with self.condition:
                    if self.stopped:
                        self.condition.wait()
            
                if self.terminate:
                    break
                
                print("\nStop Flying\n")
                self.bebop.loop_breaker = True
                self.bebop.cancel_move_relative()
                self.bebop.loop_breaker = False
            
            print("Avoidance thread done\n")
        except:
            print("Error in Avoidance class\n")
            traceback.print_exc()
            print("\n\nEmergency land the drone")
            self.bebop.safe_land(5)
            self.bebop.disconnect()
            os._exit(1)
    
    def pause(self):
        self.stopped = True

    def resume(self):
        with self.condition:
            self.stopped = False
            self.condition.notify()