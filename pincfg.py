import RPi.GPIO as GPIO # pylint: disable=import-error

RED_LED_PIN = 11
GREEN_LED_PIN = 15
BLUE_LED_PIN = 22

CLK_PIN = 16
DIO_PIN = 18

GREEN_BUTTON_PIN = 38 
YELLOW_BUTTON_PIN = 36
RED_BUTTON_PIN = 40

GREEN = 0
YELLOW = 1
RED = 2

GPIO.setwarnings(False) # Ignore warning for now
GPIO.setmode(GPIO.BOARD) # Use physical pin numbering
GPIO.setup(GREEN_BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # Set pin 10 to be an input pin and set initial value to be pulled low (off)
GPIO.setup(YELLOW_BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) 
GPIO.setup(RED_BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) 