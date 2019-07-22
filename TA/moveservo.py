import RPi.GPIO as GPIO
import time

servo = 22

def setGpio():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(servo,GPIO.OUT)
    p=GPIO.PWM(servo,50)
    return p

def opendoor():
    p = setGpio()
    p.start(6.3)
    time.sleep(1)
    p.stop()
    GPIO.cleanup()
    time.sleep(1)
    
def closedoor():
    p = setGpio()
    p.start(2.3)
    time.sleep(1)
    p.stop()
    GPIO.cleanup()