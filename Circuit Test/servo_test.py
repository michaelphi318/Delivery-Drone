import time
import board
import pwmio
from adafruit_motor import servo

pwm = pwmio.PWMOut(board.D1, frequency=50,  duty_cycle=5)

dropper = servo.Servo(pwm) #servo object

while True:
    dropper.angle = 0
    time.sleep(5)

    dropper.angle = 90
    time.sleep(5)

    dropper.angle = 180
    time.sleep(10)

    #for angle in range(0, 180, 1):  # 0 - 180 deg step of 1
     #   dropper.angle = angle
      #  time.sleep(0.05)
    #for angle in range(180, 0, -1): # 180 - 0 deg step of 1 (reversed)
     #   dropper.angle = angle
      #  time.sleep(0.05)
