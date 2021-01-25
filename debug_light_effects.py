import light_effects as leff
from pincfg import * # pylint: disable=unused-wildcard-import
import time

DEBUG = True

effect = leff.BEDTIME

def debug_press(channel):
    leff.start(effect)

if DEBUG: 
    GPIO.add_event_detect(GREEN_BUTTON_PIN,GPIO.RISING,callback=debug_press) 

while True:
    print("Debugging...") 
    time.sleep(15)