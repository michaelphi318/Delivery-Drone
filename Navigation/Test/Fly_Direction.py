from multiprocessing.sharedctypes import Value
from pyparrot.Bebop import Bebop
import math
import signal

def handler(signum, frame):
    bebop.safe_land(10)

    print("DONE - disconnecting")
    bebop.disconnect()
    exit(1)

#connects the ctrl+C interrupt to the function
signal.signal(signal.SIGINT, handler)

bebop = Bebop()

print("connecting")
success = bebop.connect(10)
print(success)

print("sleeping")
bebop.smart_sleep(5)

bebop.ask_for_state_update()

bebop.safe_takeoff(5)

while True:
    try:
        #d = int(input("Enter distance: "))
        p = float(input("Enter max pitch: "))
        v = float(input("Enter max_tilt: "))
        # a = float(input("Enter acceleration: "))
        bebop.max_tilt(p)
        bebop.max_horizontal_speed(v)
        # bebop.max_tilt_acceleration(a)

        #bebop.max_tilt_acceleration(a)

        #bebop.fly_direct(roll=0, pitch=p, yaw=0, vertical_movement=0, duration=t)
        bebop.move_relative(10,0,0,0)
    except ValueError:
        print("Input invalid")
