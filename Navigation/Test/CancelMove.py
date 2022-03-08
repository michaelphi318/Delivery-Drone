from pyparrot.Bebop import Bebop
import sys, signal
from threading import Thread, Condition
import time
from math import radians, cos, sin, asin, atan, sqrt, pi


#---------------------------Threads----------------------------

# Threads via inheritance
# Arrive: Drone will use this thread to navigate to location
# Avoidance: Drone will use this thread to avoid obstacles

class Arrive(Thread):
    def __init__(self):
        super().__init__()
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
            # print("Flying")
            bebop.move_relative(10, 0, 0, 0)
    
    def pause(self):
        self.stopped = True

    def resume(self):
        with self.condition:
            self.stopped = False
            self.condition.notify()

class Avoidance(Thread):
    def __init__(self):
        super().__init__()
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
            # print("Stop Flying")
            bebop.cancel_move_relative()
    
    def pause(self):
        self.stopped = True

    def resume(self):
        with self.condition:
            self.stopped = False
            self.condition.notify()
#--------------------------------------------------------------

#------------------------Test case-----------------------------
def test():
    #---------------------Declare threads----------------------
    threads = []
    t1 = Arrive()
    t2 = Avoidance()
    threads.append(t1)
    threads.append(t2)
    #----------------------------------------------------------

    #---------------------Execute threads----------------------
    # for thread in threads:
    #     thread.start()
    t1.start()
    t2.start()
    
    # imediately pause Avoidance thread
    t1.resume()
    t2.pause()

    # Test case
    for i in range(3):
        print("Iteration %d" % (i + 1))
        t1.resume()
        t2.pause()
        time.sleep(0.5)
        t1.pause()
        t2.resume()
        time.sleep(0.5)
        t1.resume()
        t2.pause()
        print()
    #----------------------------------------------------------

    #--------------Disconnect and Land the drone---------------
    bebop.safe_land(5)
    bebop.disconnect()
    sys.exit(0)
    #----------------------------------------------------------

#--------------------------------------------------------------


#-------------------------Main---------------------------------
if __name__ == "__main__":

    #---------------------Connect and Fly----------------------
    bebop = Bebop()
    print("Connecting to the drone\n")
    success = bebop.connect(10)
    print(success)

    # if not success:
    #     print("Connection failed\n")
    #     sys.exit(1)
        
    # print("Sleeping")
    bebop.smart_sleep(3)

    # take off
    bebop.safe_takeoff(10)
    #---------------------------------------------------------

    #------------------------Test-----------------------------
    try:
        test()
    except:
        bebop.safe_land(5)
        bebop.disconnect()
    finally:
        sys.exit(1)
    #---------------------------------------------------------

#-------------------------------------------------------------


#-----------------------Old shit------------------------------
# def t1():
#     bebop.move_relative(15, 0, 0, 0)
#     # bebop.smart_sleep(1)

# def t2():
#     time.sleep(0.3)
#     # bebop.smart_sleep(1)
#     bebop.cancel_move_relative()
    

# if __name__ == "__main__":
#     bebop = Bebop()
#     trigger = False
    
#     print("Connecting to the drone\n")
#     success = bebop.connect(10)
#     print(success)

#     # if not success:
#     #     print("Connection failed\n")
#     #     sys.exit(1)
    
#     # print("Sleeping")
#     bebop.smart_sleep(3)

#     # take off
#     bebop.safe_takeoff(10)

#     # create threads
#     thread1 = Thread(target=t1, args=())
#     thread2 = Thread(target=t2, args=())

#     thread1.start()
#     thread2.start()

#     thread1.join()
#     thread2.join()

#     # bebop.move_relative(10, 0, 0, 0)
#     # bebop.smart_sleep(1)
#     # bebop.cancel_move_relative()
#     # bebop.smart_sleep(1)

#     bebop.safe_land(5)
#     bebop.disconnect()
#----------------------------------------------------------
