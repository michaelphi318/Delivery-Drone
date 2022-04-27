from controller import DroneController
from logger import Logger
import sys, os, datetime


if __name__ == "__main__":
    bebopController = DroneController()
    path = os.path.dirname(os.path.realpath(__file__)) + "/log.txt"
    sys.stdout = Logger(path)
    sys.stderr = sys.stdout
    
    print(datetime.date.today().strftime("\n\n%d/%m/%Y"))
    print(datetime.datetime.now().strftime("%H:%M:%S"))
    bebopController.droneConnect()
    bebopController.droneCalibrate()
    bebopController.droneTakeOff()
    bebopController.droneAutonomousControl()