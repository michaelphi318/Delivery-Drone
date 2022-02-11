import signal
import time
from pyparrot.Bebop import Bebop

#function that gets called when ctrl+C interrupt occurs
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

bebop.safe_takeoff(10)

while True:
    bebop.smart_sleep(1)

