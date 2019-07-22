import RPi.GPIO as GPIO
import RPi.GPIO as GPIO

LedPin = 13

def setup():
    GPIO.setmode(GPIO.BOARD)       
    GPIO.setup(LedPin, GPIO.OUT)   
    GPIO.output(LedPin, GPIO.HIGH) 

def nyalakan():
    setup()
    GPIO.output(LedPin, GPIO.HIGH)  
    

def matikan():
    setup()
    GPIO.output(LedPin, GPIO.LOW)   
    GPIO.cleanup()

nyalakan()