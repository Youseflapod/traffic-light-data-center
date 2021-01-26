import light_effects as leff
from pincfg import * # pylint: disable=unused-wildcard-import
import time

DEBUG = True

currEffect = 0

def debug_press(channel):
    global currEffect
    print(f'Current Effect: {currEffect}')
    leff.start(currEffect)
    currEffect += 1
    if currEffect == leff.DEMO_MODE:
        currEffect = 0

if DEBUG: 
    GPIO.add_event_detect(GREEN_BUTTON_PIN,GPIO.RISING,callback=debug_press) 

while True:
    print("Debugging...") 
    time.sleep(15)