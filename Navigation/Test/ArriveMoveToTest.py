from pyparrot.Bebop import Bebop
from math import degrees, radians
import signal, sys


LATITUDE_DESTINATION = 39.96146904165966
LONGITUDE_DESTINATION = -75.18767610000323
ALTITUDE_DESTINATION = 30

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

    # print battery
    print("Battery : " + str(bebop.sensors.battery))

    print("Take off\n")
    bebop.safe_takeoff(10)

    # move to destination
    lat = degrees(LATITUDE_DESTINATION)
    lon = degrees(LONGITUDE_DESTINATION)
    alt = ALTITUDE_DESTINATION
    print("Latitude: " + str(lat) + " degree")
    print("Longitude: " + str(lon) + " degree")
    print("Altitude: " + str(alt) + " m")
    bebop.move_to(lat, lon, alt, "TO_TARGET")

    # Land
    print("\nPrepare for Landing\n")
    bebop.safe_land(5)
    print("DONE - Disconnecting")
    bebop.disconnect()
    sys.exit(0)