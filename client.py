from pyparrot.Bebop import Bebop
from termcolor import cprint, colored
import multiprocessing as mp
from _thread import *
import cv2
import math, time
from datetime import datetime
from geographiclib.geodesic import Geodesic
import geopy.distance

class Event:
    def __init__(self):
        self.listeners = []
    
    def __iadd__(self, listener):
        self.listeners.append(listener)
    
    def actionPerformed(self, *args, **kwargs):
        for listener in self.listeners:
            listener(*args, **kwargs)

class DroneController:
    def __init__(self, bebop, event):
        self.bebop = bebop
        self.event = event

    def connect(self):
        return self.bebop.connect(5)
    
    def disconnect(self):
        if self.connect():
            self.bebop.disconnect()

    def collisionAvoidance(self):
        return
    
    def gpsTracking(self):
        return

    def land(self):
        if self.connect():
            self.bebop.safe_land()

    
if __name__ == "__main__":
    bebop = Bebop()
    event = Event()
    controller = DroneController(bebop, event)

    if controller.connect():
        controller.bebop.smart_sleep(3)
        controller.bebop.ask_for_state_update()
    
    


