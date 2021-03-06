from pyparrot.Bebop import Bebop
import sys, os, time
import signal

def handler(signum, frame):
    # bebop.safe_land(10)
    # print("Emergency landing protocol - disconnecting")
    bebop.disconnect()
    sys.exit(1)

def writeFile(mode, Lat_avg, Lon_avg, Alt_avg):
    f = open(os.path.dirname(__file__) + "/../gps.txt", mode)
    f.writelines([str(Lat_avg) + "\n", str(Lon_avg) + "\n", str(Alt_avg)])
    print("File written")
    f.close()

def connect():
    print("Connecting to the drone\n")
    success = bebop.connect(5)

    if not success:
        print("Connection failed")
        sys.exit(1)
            
    bebop.smart_sleep(2)

def disconnect():
    print("DONE - disconnecting")
    bebop.disconnect()
    sys.exit(0)

def calibrate():
    # flat trim 
    start_time = time.time()
    bebop.flat_trim(2)
    end_time = time.time()
    print("Flat trim finished after %.2f" % (end_time - start_time))

def precisionTest():
    Lat_min = 2000
    Lat_max = -2000
    Lon_min = 2000
    Lon_max = -2000
    Alt_min = 2000
    Alt_max = -2000
    Alt_sum = 0
    Lon_sum = 0
    Lat_sum = 0

    #Takes 60 samples of gps location and saves the maximum and minimum values recorded
    for i in range(0,60):
        print("Sample number: {}".format(i))
        Lat = bebop.sensors.sensors_dict["GpsLocationChanged_latitude"]
        print("Latitude:  " + str(Lat))
        Lon = bebop.sensors.sensors_dict["GpsLocationChanged_longitude"]
        print("Longitude: " + str(Lon))
        Alt = bebop.sensors.sensors_dict["GpsLocationChanged_altitude"]
        print("Altitude:  " + str(Alt) + "\n")
        Alt_sum += Alt
        Lon_sum += Lon
        Lat_sum += Lat
        if(Lat_min > Lat):
            Lat_min = Lat
        if(Lat_max < Lat):
            Lat_max = Lat
        if(Lon_min > Lon):
            Lon_min = Lon
        if(Lon_max < Lon):
            Lon_max = Lon
        if(Alt_min > Alt):
            Alt_min = Alt
        if(Alt_max < Alt):
            Alt_max = Alt
        bebop.smart_sleep(0.5)

    #Calculates the range of the gps location in each direction measured in feet
    Lat_precision = (Lat_max - Lat_min) * 364000
    Lon_precision = (Lon_max - Lon_min) * 288200
    Alt_precision = (Alt_max - Alt_min) * 3.28084
    Lat_avg = Lat_sum/60
    Lon_avg = Lon_sum/60
    Alt_avg = Alt_sum/60
    print("Latitude Precision: " + str(Lat_precision) + " feet")
    print("Longitdue Precision: " + str(Lon_precision) + " feet")
    print("Altitude Precision: " + str(Alt_precision) + " feet")
    print("Latitude Average: " + str(Lat_avg) + " feet")
    print("Longitdue Average: " + str(Lon_avg) + " feet")
    print("Altitude Average: " + str(Alt_avg) + " feet")

    return Lat_avg, Lon_avg, Alt_avg

def disconnect():
    print("DONE - disconnecting")
    bebop.safe_land(2)
    bebop.disconnect()


if __name__ == "__main__":
    signal.signal(signal.SIGINT, handler)
    bebop = Bebop()
    lat = lon = alt = 0.0
    
    connect()
    calibrate()

    # GPS for destination
    lat, lon, alt = precisionTest()
    writeFile("w", lat, lon, alt)

    # GPS for origin (uncomment to use)
    # time.sleep(30)
    # lat, lon, alt = precisionTest()
    # writeFile("a", lat, lon)

    disconnect()