# Connect to a remote sensing service over Bluetooth Low-Energy (BLE).  This
# script runs in Python 3 on a desktop or laptop.  It scans for a connection,
# then prints incoming data to the console until the connection breaks. The
# data is then evaluated to see if the obstacle avoidance protocol needs to be
# initiated. 

# It assumes the following packages have been installed:
#
#  pip3 install adafruit-blinka-bleio
#  pip3 install adafruit-circuitpython-ble

# ----------------------------------------------------------------
# Import the Adafruit Bluetooth library, part of Blinka.  Technical reference:
# https://circuitpython.readthedocs.io/projects/ble/en/latest/api.html

from concurrent.futures import thread
from adafruit_ble import BLERadio
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.services.nordic import UARTService
import signal
import sys
import asyncio
import platform
from threading import Thread

sensorData = [] #Global list of distance read from each sensor
avoidanceTrigger = False #Boolean to see if obstacle avoidance should run
distanceThreshold = 60
def t1():
    global trigger
    global packageDelivery
    ble = BLERadio()
    uart_connection = None
    # uart = UARTService()
    while True:
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
                sensorData = uart_service.readline().decode("utf-8").rstrip()

                #If obstacle avoidance is not running then it will check to see if it should run
                if not avoidanceTrigger:
                    for i in sensorData:
                        if i < distanceThreshold:
                            avoidanceTrigger = True

def obstacleAvoidance():
    while True:
        if avoidanceTrigger:
            if sensorData[0] < distanceThreshold and sensorData[2] < distanceThreshold:
                print("Move right")
                print("Move forward")
            else:
                print("Move up")
            if sensorData[1] < distanceThreshold and sensorData[2] < distanceThreshold:
                print("Move left")
                print("Move forward")
            else:
                print("Move up")
            if sensorData[2] < distanceThreshold:
                print("Move up")
            
            #Checks if obstacle avoidance still needs to run
            avoidanceCheck = True
            for i in sensorData:
                if i < distanceThreshold:
                    avoidanceCheck = False
            if avoidanceCheck:
                avoidanceTrigger = False
            
            


if __name__ == "__main__":
    trigger = False
    packageDelivery = False
    thread1 = Thread(target=t1)
    thread2 = Thread(target=obstacleAvoidance)

    thread1.start()
    thread2.start()

    thread1.join()
    thread2.join()
