import light_effects as leff
from pincfg import * # pylint: disable=unused-wildcard-import

DEBUG = True

effect = leff.BEDTIME

def debug_press():
    leff.start(effect)

if DEBUG: 
    GPIO.add_event_detect(GREEN_BUTTON_PIN,GPIO.RISING,callback=debug_press) 
    