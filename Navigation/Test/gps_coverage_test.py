from pyparrot.Bebop import Bebop
from threading import Thread
import signal, sys, os
from math import radians


def handler(signum, frame):
    bebop.safe_land(10)

    print("DONE - disconnecting")
    bebop.disconnect()
    exit(1)

def gps():
    while True:
        lat = bebop.sensors.sensors_dict["GpsLocationChanged_latitude"]
        lon = bebop.sensors.sensors_dict["GpsLocationChanged_longitude"]
        alt = bebop.sensors.sensors_dict["GpsLocationChanged_altitude"]
    
        if lat == 500 or lon == 500 or alt == 500:
            print("GPS is 500, issue e command to land the drone (recommend)")

if __name__ == "__main__":
    #connects the ctrl+C interrupt to the function
    signal.signal(signal.SIGINT, handler)

    bebop = Bebop()

    print("Connecting")
    success = bebop.connect(5)

    if not success:
        print("Connection failed\n")
        sys.exit(1)

    bebop.smart_sleep(2)
    bebop.safe_takeoff(5)

    thread1 = Thread(target=gps, args=())
    thread1.start()

    while True:
        try:
            command = input("\nEnter command: ")

            if command.lower() == "m":
                i = float(input("Enter distance to go forward: "))
                bebop.move_relative(i, 0, 0, 0)
            elif command.lower() == "r":
                i = float(input("Enter rotation angle: "))
                bebop.move_relative(0, 0, 0, radians(i))
            elif command.lower() == "v":
                i = float(input("Enter distance to go vertical (negative for up, positive for down): "))
                bebop.move_relative(0, 0, i, 0)
            elif command.lower() == "e":
                break
            else:
                print("Input invalid")
            # bebop.max_tilt(p)
            # bebop.max_horizontal_speed(v)
            # bebop.max_tilt_acceleration(a)
            #bebop.max_tilt_acceleration(a)
            #bebop.fly_direct(roll=0, pitch=p, yaw=0, vertical_movement=0, duration=t)
            # bebop.move_relative(0, 0, -5, 0)
            # bebop.move_relative(5,0,0,0)
        except ValueError:
            print("Input invalid")

    # while True:
    #     bebop.smart_sleep(1)

    bebop.safe_land(5)
    bebop.disconnect()
    sys.exit(0)