# Write your code here :-)
import time
import board

import adafruit_hcsr04

from analogio import AnalogIn

#trigger = AnalogIn(board.A6).value
#echo = AnalogIn(board.A4).value
sonar1 = adafruit_hcsr04.HCSR04(trigger_pin=board.D1, echo_pin=board.D2)
sonar2 = adafruit_hcsr04.HCSR04(trigger_pin=board.D1, echo_pin=board.D3)

while True:
    try:
        print((sonar1.distance,))
        print((sonar2.distance,))
    except RuntimeError:
        print("Retrying!")
    time.sleep(0.1)

