from pyparrot.Bebop import Bebop
from math import degrees, radians
import signal, sys


LATITUDE_DESTINATION = 39.96111695555687
LONGITUDE_DESTINATION = -75.18761155555504
ALTITUDE_DESTINATION = 26.0

def handler(signum, frame):
    bebop.safe_land(10)
    print("Emergency landing protocol - disconnecting")
    bebop.disconnect()
    sys.exit(1)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, handler)

    bebop = Bebop()
    
    print("Connecting to the drone\n")
    success = bebop.connect(10)
    print(success)

    if not success:
        print("Connection failed\n")
        sys.exit(1)
    
    # print("Sleeping")
    bebop.smart_sleep(1)

    print("Take off\n")
    bebop.safe_takeoff(10)

    # move to destination
    lat = degrees(LATITUDE_DESTINATION)
    lon = degrees(LONGITUDE_DESTINATION)
    alt = ALTITUDE_DESTINATION
    print("Latitude: " + str(lat) + " degree")
    print("Longitude: " + str(lon) + " degree")
    print("Altitude: " + str(alt) + " m")
    print("Move to destination")
    bebop.move_to(lat, lon, alt, "abc", 0.5)
    print("Sleeping")
    bebop.smart_sleep(1)
    # bebop.move_to(lat, lon, alt, "NONE")
    
    # move 1m ahead
    # print("Move relative")
    # bebop.move_relative(1,0,0,0)
    # print("Sleeping")
    # bebop.smart_sleep(1)

    # Land
    print("\nPrepare for Landing\n")
    bebop.safe_land(5)
    print("DONE - Disconnecting")
    bebop.disconnect()
    sys.exit(0)