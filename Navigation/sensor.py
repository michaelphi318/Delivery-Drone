from pyparrot.Bebop import Bebop
from threading import Thread
from adafruit_ble import BLERadio
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.services.nordic import UARTService
import sys, os, time, traceback


class NavigationSensor(Thread):
    def __init__(self, bebop):
        super().__init__()
        if isinstance(bebop, Bebop):
            self.bebop = bebop
        self.isTerminated = False
        self.sensors = []
        self.distanceThreshold = 60
        self.isAvoidanceTriggered = False

    def getAvoidanceCase(self):
        res = ""

        for sensor in self.sensors:
            if sensor < self.distanceThreshold:
                res += "1"
            else:
                res += "0"

        return res
    
    def setAvoidanceTrigger(self):
        self.isAvoidanceTriggered = any(i < self.distanceThreshold for i in self.sensors)

    def run(self):
        try:
            ble = BLERadio()
            uart_connection = None

            while not self.isTerminated:
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
                        data = uart_service.readline().decode("utf-8").rstrip()

                        if data:
                            self.sensors = list(map(int, data.split(',')))
                        
                        self.setAvoidanceTrigger()
        except:
            print("\nError in Sensor class\n")
            traceback.print_exc()
            print("\n\nEmergency land the drone")
            self.bebop.safe_land(5)
            self.bebop.disconnect()
            os._exit(1)


# if __name__ == "__main__":
#     navi = NavigationSensor()
#     navi.start()
#     navi.join()