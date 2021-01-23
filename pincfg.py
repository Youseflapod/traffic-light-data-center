import RPi.GPIO as GPIO

GREEN_PIN = 20  
YELLOW_PIN = 20
RED_PIN = 20

GREEN = 0
YELLOW = 1
RED = 2

GPIO.setwarnings(False) # Ignore warning for now
GPIO.setmode(GPIO.BOARD) # Use physical pin numbering
GPIO.setup(10, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # Set pin 10 to be an input pin and set initial value to be pulled low (off)