from pyparrot.Bebop import Bebop
import sys, signal
from threading import Thread, Condition
import time
from math import radians, cos, sin, asin, atan, sqrt, pi


class Avoidance(Thread):
    def __init__(self, bebop):
        super().__init__()
        self.bebop = bebop
        # python program exits when only daemon threads are left
        # self.daemon = True
        self.stopped = True
        self.condition = Condition()

    def run(self):
        self.resume()

        while True:
            with self.condition:
                if self.stopped:
                    self.condition.wait()

            print("Stop Flying")
            self.bebop.loop_breaker = True
            self.bebop.cancel_move_relative()
    
    def pause(self):
        self.stopped = True

    def resume(self):
        with self.condition:
            self.stopped = False
            self.condition.notify()