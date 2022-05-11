from pyparrot.Bebop import Bebop
from threading import Thread, Condition
from math import pi
from sensor import NavigationSensor
from logger import Logger
import sys, os, time, traceback, datetime


# class Avoidance(Thread):
class Avoidance():
    def __init__(self, bebop):
        # super().__init__()
        if isinstance(bebop, Bebop):
            self.bebop = bebop
        # self.isPaused = True
        # self.isTerminated = False
        # self.condition = Condition()
        self.navi = NavigationSensor(self.bebop)

    def turnRight(self):
        while self.navi.isAvoidanceTriggered:
        # print("Turn right 10 degrees")
            self.bebop.move_relative(0, 0, 0, 10 * pi / 180)
            time.sleep(0.1)
        
        time.sleep(2)
        
        if self.navi.isAvoidanceTriggered:
            self.turnRight()
    
    def turnLeft(self):
        while self.navi.isAvoidanceTriggered:
        # print("Turn left 10 degrees")
            self.bebop.move_relative(0, 0, 0, -10 * pi / 180)
            time.sleep(0.1)
        
        time.sleep(5)

        if self.navi.isAvoidanceTriggered:
            self.turnLeft()

    def moveForward(self):
        if self.navi.isAvoidanceTriggered:
            print("Not clear to move forward")
        else:
        # print("Move Forward")
            self.bebop.move_relative(1, 0, 0, 0)

    def moveUp(self):
        while self.navi.isAvoidanceTriggered:
        # print("Move up")
            self.bebop.move_relative(0, 0, -1, 0)
    
    def moveDown(self):
        while self.navi.isAvoidanceTriggered:
        # print("Move down")
            self.bebop.move_relative(0, 0, 0.5, 0)
    
    # def run(self):
    #     try:
    #         while not self.isTerminated:
    #             with self.condition:
    #                 if self.isPaused:
    #                     self.condition.wait()

    #             self.bebop.loop_breaker = True
    #             # print("Cancel move relative")
    #             # self.bebop.cancel_move_relative()
            
    #         print("Avoidance thread done\n")
    #     except:
    #         print("Error in Avoidance class\n")
    #         traceback.print_exc()
    #         print("\n\nEmergency land the drone")
    #         self.bebop.safe_land(5)
    #         self.bebop.disconnect()
    #         os._exit(1)
    
    # def pause(self):
    #     self.isPaused = True

    # def resume(self):
    #     with self.condition:
    #         self.isPaused = False
    #         self.condition.notify()


# if __name__ == "__main__":
#     path = os.path.dirname(os.path.realpath(__file__)) + "/log.txt"
#     # sys.stdout = Logger(path)
#     # sys.stderr = sys.stdout
#     sys.stderr = Logger(path)
#     avoidanceThread = Avoidance(Bebop())
#     cases = {"000" : [avoidanceThread.moveDown], 
#                 "001" : [avoidanceThread.turnRight, avoidanceThread.moveForward],
#                 "010" : [avoidanceThread.turnLeft, avoidanceThread.moveForward],
#                 "011" : [avoidanceThread.turnLeft, avoidanceThread.moveForward],
#                 "100" : [avoidanceThread.turnRight, avoidanceThread.moveForward],
#                 "101" : [avoidanceThread.turnRight, avoidanceThread.moveForward],
#                 "110" : [avoidanceThread.turnLeft, avoidanceThread.moveForward],
#                 "111" : [avoidanceThread.turnRight, avoidanceThread.moveForward]}

#     print(datetime.date.today().strftime("\n\n%d/%m/%Y"))
#     print(datetime.datetime.now().strftime("%H:%M:%S"))
#     avoidanceThread.navi.start()

#     while True:
#         time.sleep(5)
#         print(avoidanceThread.navi.sensors)
#         case = avoidanceThread.navi.getAvoidanceCase()
#         print("Case %s" % case)

#         if avoidanceThread.navi.sensors[3] < avoidanceThread.navi.distanceThreshold and avoidanceThread.navi.isAvoidanceTriggered:
#             if case in cases.keys():
#                 for command in cases.get(case):
#                     command()
#                 print("Done\n")
#             else:
#                 print("Case not in dictionary")
#         elif avoidanceThread.navi.sensors[3] < avoidanceThread.navi.distanceThreshold and not avoidanceThread.navi.isAvoidanceTriggered:
#             avoidanceThread.moveDown()
#             print("Done\n")
#         elif avoidanceThread.navi.sensors[3] > avoidanceThread.navi.distanceThreshold:
#             avoidanceThread.moveUp()