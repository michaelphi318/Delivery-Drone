from pyparrot.Bebop import Bebop
from threading import Thread, Condition


class Avoidance(Thread):
    def __init__(self, bebop):
        super().__init__()
        self.daemon = True
        if isinstance(bebop, Bebop):
            self.bebop = bebop
        self.stopped = True
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