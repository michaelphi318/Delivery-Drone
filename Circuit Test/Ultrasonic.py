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

# echo2 = DigitalInOut(board.D2)
# echo2.direction = Direction.INPUT
while True:
#     echo1.clear()
#     trigger.value = True
#     time.sleep(0.00001)
#     trigger.value = False


#     pulselen = None
#     timestamp = time.monotonic()
#     echo1.resume()
#     while not echo1:
#         if time.monotonic() - timestamp > 0.1:
#             echo1.pause()
#             raise RuntimeError("Timed out")
#     echo1.pause()
#     pulselen = echo1[0] # convert to us to match pulseio

    try:
        #print("Sideway Object Detection: %f m"%(sonar1.distance))
        print("Forward Object Detection: %f m"%(sonar2.distance))
        time.sleep(0.5)
    except RuntimeError:
        print("400")
        time.sleep(0.1)
