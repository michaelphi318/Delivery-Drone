from pyparrot.Bebop import Bebop
from DroneController import *
import signal


if __name__ == "__main__":
    def emergencyExit(signum, frame):
        bebop.safe_land(10)
        print("Safe land - Disconnecting")
        bebop.disconnect()
        sys.exit(1)

    signal.signal(signal.SIGINT, emergencyExit)

    bebop = Bebop()
    controller = DroneController(bebop)
    
    controller.begin(2)
    controller.run()

    sys.exit(0)