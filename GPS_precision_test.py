from pyparrot.Bebop import Bebop

bebop = Bebop()
print("connecting")
success = bebop.connect(10)
print(success)

print("sleeping")
bebop.smart_sleep(5)
Lat_min = 200
Lat_max = 0
Lon_min = 200
Lon_max = 0
Alt_min = 200
Alt_max = 0

#Takes 60 samples of gps location and saves the maximum and minimum values recorded
for i in range(0,60):
    print("Sample number: {}".format(i))
    Lat = bebop.sensors.sensors_dict["GpsLocationChanged_latitude"]
    print("Latitude:  " + str(Lat))
    Lon = bebop.sensors.sensors_dict["GpsLocationChanged_longitude"]
    print("Longitude: " + str(Lon))
    Alt = bebop.sensors.sensors_dict["GpsLocationChanged_altitude"]
    print("Altitude:  " + str(Alt) + "\n")
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
    bebop.smart_sleep(1)

#Calculates the range of the gps location in each direction measured in feet
Lat_precision = (Lat_max - Lat_min) * 364000
Lon_precision = (Lon_max - Lon_min) * 288200
Alt_precision = (Alt_max - Alt_min) * 3.28084
print("Latitude Precision: " + str(Lat_precision) + " feet")
print("Longitdue Precision: " + str(Lon_precision) + " feet")
print("Altitude Precision: " + str(Alt_precision) + " feet")

print("DONE - disconnecting")
bebop.disconnect()