'''Main function

Autonomously fly the drone to the destination, 
drop off the package, and return to origin location
'''

from controller import DroneController
from logger import Logger
import sys, os, datetime


def main():
    # Initialize the controller
    # Initialize the console log file path to read stdout and stderr
    bebopController = DroneController()
    path = os.path.dirname(os.path.realpath(__file__)) + "/log.txt"
    sys.stdout = Logger(path)
    sys.stderr = sys.stdout
    
    # Print date and time to the log file
    print(datetime.date.today().strftime("\n\n%d/%m/%Y"))
    print(datetime.datetime.now().strftime("%H:%M:%S"))
    
    # Connect to the drone
    bebopController.droneConnect()

    # Calibrate the drone
    bebopController.droneCalibrate()

    # Take off the drone
    bebopController.droneTakeOff()

    # Autonomously control the drone
    bebopController.droneAutonomousControl()

if __name__ == "__main__":
    main()