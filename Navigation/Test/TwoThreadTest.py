from pyparrot.Bebop import Bebop
import sys, signal
from threading import Thread
from statistics import mean


LATITUDE_DESTINATION = 39.96147141121459
LONGITUDE_DESTINATION = -75.18766440922718

def handler(signum, frame):
    bebop.safe_land(10)
    print("Emergency landing protocol - disconnecting")
    bebop.disconnect()
    sys.exit(1)

def t1(list):
    while True:
        lat = bebop.sensors.sensors_dict["GpsLocationChanged_latitude"]
        lon = bebop.sensors.sensors_dict["GpsLocationChanged_longitude"]
        alt = bebop.sensors.sensors_dict["GpsLocationChanged_altitude"]
        bebop.smart_sleep(0.1)
        list.append([lat, lon, alt])
        list.pop(0)

        lat_avg = (list[0][0] + list[1][0] + list[2][0]) / 3
        lon_avg = (list[0][1] + list[1][1] + list[2][1]) / 3
        alt_avg = (list[0][2] + list[1][2] + list[2][2]) / 3

        print("Lat: " + str(lat_avg))
        print("Lon: " + str(lon_avg))
        print("Alt: " + str(alt_avg))


def t2(list):
    while True:
        bebop.move_relative(0.5, 0, 0, 0)
        bebop.smart_sleep(0.1)

def t3():
    while True:
        input = input("Enter your command: ")
        if (input.lower() == "q"):
            bebop.safe_land(10)
            print("Emergency landing protocol - disconnecting")
            bebop.disconnect()
            sys.exit(1)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, handler)

    bebop = Bebop()
    gpsList = [[0, 0, 0]] * 3
    
    print("Connecting to the drone\n")
    success = bebop.connect(10)
    print(success)

    if not success:
        print("Connection failed\n")
        sys.exit(1)
    
    # print("Sleeping")
    bebop.smart_sleep(1)

    bebop.safe_takeoff(10)
    bebop.smart_sleep(2)

    t1 = Thread(target=t1, args=(gpsList,))
    t2 = Thread(target=t2, args=(gpsList,))

    t1.start()
    t2.start()

    t1.join()
    t2.join()