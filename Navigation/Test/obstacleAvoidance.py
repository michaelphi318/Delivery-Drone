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

from numpy import double

sensorData = [400, 400, 400] #Global list of distance read from each sensor

distanceThreshold = 60
global avoidanceTrigger
def t1():
    global trigger
    global packageDelivery
    global avoidanceTrigger
    global sensorData
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
                data = uart_service.readline().decode("utf-8").rstrip()
                if data:
                    sensorData = list(map(int, data.split(',')))
                    print(sensorData)
                #If obstacle avoidance is not running then it will check to see if it should run
                if not avoidanceTrigger:
                    for i in sensorData:
                        if i < distanceThreshold:
                            avoidanceTrigger = True

def obstacleAvoidance():
    global avoidanceTrigger
    global sensorData
    global distanceThreshold

    while True:
        if avoidanceTrigger:
            if(sensorData[0] < distanceThreshold):
                left = '1'
            else:
                left = '0'
            if(sensorData[1] < distanceThreshold):
                right = '1'
            else:
                right = '0'
            if(sensorData[2] < distanceThreshold):
                front = '1'
            else:
                front = '0'
            
            key = left + right + front
            print(sensorData)
            print(left, right, front)
          
            
            if left:
                if not front and not right:
                    print("Move right")
                elif not front and right:
                    print("Move forward")        
                elif front and not right:
                    print("Move right and go forward")
                elif front and right:
                    print("Move up")
            elif right:
                if not left and not front:
                    print("Move left")
                elif not left and front:
                    print("Move Left and go foward")
            elif front:
                if not left and not right:
                    print("Go right or left or up")
            else:
                print("Go forward")


            #Checks if obstacle avoidance still needs to run
            avoidanceTrigger = not all(i >= distanceThreshold for i in sensorData)
            
            


if __name__ == "__main__":
    trigger = False
    
    avoidanceTrigger = False #Boolean to see if obstacle avoidance should run
    packageDelivery = False
    thread1 = Thread(target=t1)
    thread2 = Thread(target=obstacleAvoidance)

    thread1.start()
    thread2.start()

    thread1.join()
    thread2.join()
