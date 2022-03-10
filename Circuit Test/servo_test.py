import time
import board
import pwmio
from adafruit_motor import servo

pwm = pwmio.PWMOut(board.D0, frequency=50,  duty_cycle=5)

dropper = servo.Servo(pwm) #servo object

while True:
    dropper.angle = 148 #open position
    time.sleep(10)
    
    dropper.angle = 70 #closed
    time.sleep(1)

    #for angle in range(0, 180, 1):  # 0 - 180 deg step of 1
     #   dropper.angle = angle
      #  time.sleep(0.05)
    #for angle in range(180, 0, -1): # 180 - 0 deg step of 1 (reversed)
     #   dropper.angle = angle
      #  time.sleep(0.05)
