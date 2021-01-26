import light_effects as leff
from pincfg import * # pylint: disable=unused-wildcard-import
import time

DEBUG = False

currEffect = 0

def debug_press(channel):
    global currEffect
    print(f'Current Effect: {int(round(currEffect))}')
    leff.start(int(round(currEffect)))
    currEffect += 0.5
    if currEffect == leff.DEMO_MODE:
        currEffect = 0
    time.sleep(0.5)

if DEBUG: 
    GPIO.add_event_detect(GREEN_BUTTON_PIN,GPIO.RISING,callback=debug_press) 

while True:
    print("Debugging...") 
    time.sleep(15)