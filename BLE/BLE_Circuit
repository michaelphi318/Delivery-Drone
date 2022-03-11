import time
import board
import pwmio
from adafruit_motor import servo
import adafruit_hcsr04

from analogio import AnalogIn
from digitalio import DigitalInOut, Direction
trigger = DigitalInOut(board.D1)
sonar_front = adafruit_hcsr04.HCSR04(trigger, echo_pin=board.D9)
sonar_left = adafruit_hcsr04.HCSR04(trigger, echo_pin=board.D2)
sonar_right = adafruit_hcsr04.HCSR04(trigger, echo_pin=board.D3)
#sonar_up = adafruit_hcsr04.HCSR04(trigger, echo_pin=board.D3)

# Import the board-specific input/output library.
from adafruit_circuitplayground import cp

# Import the Adafruit Bluetooth library.  Technical reference:
# https://circuitpython.readthedocs.io/projects/ble/en/latest/api.html
from adafruit_ble import BLERadio
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.services.nordic import UARTService

# ----------------------------------------------------------------
# Initialize global variables for the main loop.

ble = BLERadio()
uart = UARTService()
advertisement = ProvideServicesAdvertisement(uart)

# Flags for detecting state changes.
advertised = False
connected  = False
front = 400
left = 400
right = 400
# The sensor sampling rate is precisely regulated using the following timer variables.
sampling_timer    = 0.0
last_time         = time.monotonic()
sampling_interval = 0.10
x = True
trigger = False
# ----------------------------------------------------------------
# Begin the main processing loop.
def drop_package():
    pwm = pwmio.PWMOut(board.D0, frequency=50,  duty_cycle=5)
    dropper = servo.Servo(pwm)
    
    dropper.angle = 148 #open position
    time.sleep(10)
    
    dropper.angle = 70 #closed
    time.sleep(1)
    
while True:
    try:
        front = sonar_front.distance
        left = sonar_left.distance
        right = sonar_right.distance
    except:
        front = 400
        left = 400
        right = 400
    # Read the accelerometer at regular intervals.  Measure elapsed time and
    # wait until the update timer has elapsed.
    now = time.monotonic()
    interval = now - last_time
    last_time = now
    sampling_timer -= interval
    if sampling_timer < 0.0:
        sampling_timer += sampling_interval

        #up = solar_up.distance
    else:
        x = True

    if not advertised:
        ble.start_advertising(advertisement)
        print("Waiting for connection.")
        advertised = True

    if not connected and ble.connected:
        print("Connection received.")
        connected = True
        cp.red_led = True

    if connected:
        if not ble.connected:
            print("Connection lost.")
            connected = False
            advertised = False
            cp.red_led = False
        else:
            if uart.readline().decode("utf-8"):
                drop_package()
                trigger = True
            if x is not None and not trigger:
                #print(b"%.3f,%.3f,%.3f\n" % (left, right, front))
                uart.write(b"%d,%d,%d\n" % (left, right, front))
                #uart.write(b"%d\n" % (sonar.distance))
