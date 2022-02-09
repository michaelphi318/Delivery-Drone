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

bepop.set_max_vertical_speed(2.5)
bebop.ask_for_state_update()

bebop.safe_takeoff(5)

cmd = 0

while True:
  cmd = int(input("Enter Velocity:"))
  bebop.fly_direct(roll=0, pitch=cmd, yaw=0, vertical_movement=0, duration=1)
