from pyparrot.Bebop import Bebop
from threading import Thread
from time import perf_counter
import sys


def avgGPS(result, n):
    def handler(index):
        lat = bebop.sensors.sensors_dict["GpsLocationChanged_latitude"]
        lon = bebop.sensors.sensors_dict["GpsLocationChanged_longitude"]
        alt = bebop.sensors.sensors_dict["GpsLocationChanged_altitude"]
        result[index] = [lat, lon, alt]

    lat_min = -2000
    lat_max = 2000
    lon_min = -2000
    lon_max = 2000
    alt_min = -2000
    alt_max = 2000
    lat_sum = 0
    lon_sum = 0
    alt_sum = 0
    result = [None] * n
    threads = [None] * n

    for i in range(n):
        threads[i] = Thread(target=handler, args=(i,))

    for thread in threads:
        thread.start()
        
    for thread in threads:
        thread.join()

    for i in range(len(result)):
        lat_sum += result[i][0]
        lon_sum += result[i][1]
        alt_sum += result[i][2]

        if (lat_min > result[i][0]):
            lat_min = result[i][0]
        if (lat_max < result[i][0]):
            lat_max = result[i][0]
        if (lon_min > result[i][1]):
            lon_min = result[i][1]
        if (lon_max < result[i][1]):
            lon_max = result[i][1]
        if (alt_min > result[i][2]):
            alt_min = result[i][2]
        if (alt_max < result[i][2]):
            alt_max = result[i][2]
        
    lat_precision = (lat_max - lat_min) * 364000
    lon_precision = (lon_max - lon_min) * 288200
    alt_precision = (alt_max - alt_min) * 3.28084
    lat_avg = lat_sum / n
    lon_avg = lon_sum / n
    alt_avg = alt_sum / n

    return lat_precision, lon_precision, alt_precision, lat_avg, lon_avg, alt_avg, result


if __name__ == "__main__":
    result = [None] * 60

    bebop = Bebop()
    print("Connecting")
    success = bebop.connect(5)
    print(success)

    print("Sleeping")
    bebop.smart_sleep(2)

    if not success:
        print("Failed")
        sys.exit(1)

    start = perf_counter()
    lat_precision, lon_precision, alt_precision, lat, lon, alt, result = avgGPS(result, len(result))
    end = perf_counter()
    time = end - start
    
    for i in range(len(result)):
        print("Iteration " + str(i))
        print("Latitude: " + str(result[i][0]))
        print("Longitude: " + str(result[i][1]))
        print("Altitude: " + str(result[i][2]) + "\n")

    print("It took " + str(time) + " seconds")

    print("Latitude Precision: " + str(lat_precision) + " feet")
    print("Longitdue Precision: " + str(lon_precision) + " feet")
    print("Altitude Precision: " + str(alt_precision) + " feet\n")

    print("Latitude Average: " + str(lat))
    print("Longitude Average: " + str(lon))
    print("Altitude Average: " + str(alt))