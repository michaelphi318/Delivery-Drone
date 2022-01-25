from pyparrot.Bebop import Bebop
import _thread
import threading
from queue import Queue
import sys
from adafruit_ble import BLERadio
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.services.nordic import UARTService


def gpsTesting(bebop, queue, stop):
    for i in range(0,61):
        if i == 60:
            stop = True
            break

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
    #queue.put(Lat_precision)
    #queue.put(Lon_precision)
    #queue.put(Alt_precision)

def bleLaptop(uart_connection, queue, stop):
    while True:
        if stop:
            break

        if not uart_connection:
            print("Trying to connect...")
            for adv in ble.start_scan(ProvideServicesAdvertisement):
                if UARTService in adv.services:
                    uart_connection = ble.connect(adv)
                    print("Connected")
                    break
            ble.stop_scan()

        if uart_connection and uart_connection.connected:
            uart_service = uart_connection[UARTService]
            while uart_connection.connected:
                print(uart_service.readline().decode("utf-8").rstrip())
                queue.put(uart_service.readline().decode("utf-8").rstrip())


if __name__ == "__main__":
    ble = BLERadio()
    uart_connection = None
    bebop = Bebop()
    success = bebop.connect(5)
    stop = False
    q = Queue()     #shared data from threads

    if (success):
        bebop.smart_sleep(5)
        bebop.ask_for_state_update()
            
        t1 = threading.Thread(target=gpsTesting, args=(bebop,q,stop,))
        t2 = threading.Thread(target=bleLaptop, args=(uart_connection,q,stop,)) 
            
        t1.start()
        t2.start()

        while stop == False:
            continue

        t1.join()
        t2.join()

        bebop.disconnect()
        sys.exit("Testing done")
