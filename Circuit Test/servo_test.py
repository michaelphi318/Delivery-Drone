import time
import board
import pwmio
from adafruit_motor import servo

pwm = pwmio.PWMOut(board.D0, frequency=50,  duty_cycle=5)

dropper = servo.Servo(pwm) #servo object

while True:
    dropper.angle = 148 #open position
    time.sleep(1)
    
    dropper.angle = 70 #closed
    time.sleep(10)
