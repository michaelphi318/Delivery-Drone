# Write your code here :-)
import time
import board
import pulseio

import adafruit_hcsr04

from analogio import AnalogIn
from digitalio import DigitalInOut, Direction


trigger = DigitalInOut(board.D1)
sonar1 = adafruit_hcsr04.HCSR04(trigger, echo_pin=board.D9)
sonar2 = adafruit_hcsr04.HCSR04(trigger, echo_pin=board.D2)
sonar3 = adafruit_hcsr04.HCSR04(trigger, echo_pin=board.D3)


# echo2 = DigitalInOut(board.D2)
# echo2.direction = Direction.INPUT
while True:

    try:
        print("Sonar 1: %f cm"%(sonar1.distance))
        print("Sonar 2: %f cm"%(sonar2.distance))
        print("Sonar 3: %f cm"%(sonar3.distance))
        time.sleep(0.25)
    except RuntimeError:
        print("400")
        time.sleep(0.1)