from pyparrot.Bebop import Bebop
from math import degrees, radians
import signal, sys


LATITUDE_DESTINATION = 39.960949649116785
LONGITUDE_DESTINATION = -75.18757379939173
ALTITUDE_DESTINATION = 0.0

def handler(signum, frame):
    bebop.safe_land(10)
    print("Emergency landing protocol - disconnecting")
    bebop.disconnect()
    sys.exit(1)

def avgGPS(bebop, n):
    lat_sum = 0
    lon_sum = 0
    alt_sum = 0

    for i in range(n):
        lat = bebop.sensors.sensors_dict["GpsLocationChanged_latitude"]
        lon = bebop.sensors.sensors_dict["GpsLocationChanged_longitude"]
        alt = bebop.sensors.sensors_dict["GpsLocationChanged_altitude"]
        bebop.smart_sleep(0.1)
    
    lat_avg = lat_sum / n
    lon_avg = lon_sum / n
    alt_avg = alt_sum / n

    return lat_avg, lon_avg, alt_avg

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
    print("Battery : "+str(bebop.sensors.battery))

    print("Take off\n")
    bebop.safe_takeoff(10)

    # move to destination
    lat = degrees(LATITUDE_DESTINATION)
    lon = degrees(LONGITUDE_DESTINATION)
    alt = ALTITUDE_DESTINATION
    bebop.move_to(lat, lon, alt, "TO_TARGET")

    # Land
    print("\nPrepare for Landing\n")
    bebop.safe_land(5)
    print("DONE - Disconnecting")
    bebop.disconnect()
    sys.exit(0)