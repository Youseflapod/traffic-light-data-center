from global_vars import * # pylint: disable=unused-wildcard-import
import logging
import light_effects
import RPi.GPIO # pylint: disable=import-error
import pigpio # pylint: disable=import-error
from pincfg import *  # pylint: disable=unused-wildcard-import
import tm1637
import time
import datetime

pi = pigpio.pi()

PWM_RANGE = 40000
pi.set_PWM_range(RED_LED_PIN, PWM_RANGE)
pi.set_PWM_range(GREEN_LED_PIN, PWM_RANGE)
pi.set_PWM_range(BLUE_LED_PIN, PWM_RANGE)

clockDisplay = tm1637.TM1637(CLK_PIN, DIO_PIN, tm1637.BRIGHT_TYPICAL)
clockDisplay.Clear()
clockDisplay.SetBrightness(CLOCK_BRIGHTNESS)

shouldDisplayBeClear = True
isDisplayActuallyClear = True
currentlySetFourNumbers = [0,0,0,0]

def set_pin_light(pin, value, brightness):
    if value > 255 or brightness > 1:
        logging.error(f'Too bright!! My eyes! Can\'t set pin {pin} to {value} with brightness {brightness}')
        raise Exception(f'Too bright!! My eyes! Can\'t set pin {pin} to {value} with brightness {brightness}')
    if value < 0 or brightness < 0:
        logging.error(f'Too dim!! My eyes? Can\'t set pin {pin} to {value} with brightness {brightness}')
        raise Exception(f'Too dim!! My eyes? Can\'t set pin {pin} to {value} with brightness {brightness}')
    realBrightness = int(PWM_RANGE * (value * float(brightness)) / 255.0)
    pi.set_PWM_dutycycle(pin, realBrightness)

def set_light_and_brightness(rgba_tuple):
    r,g,b,a = rgba_tuple
    set_pin_light(RED_LED_PIN, r, a)
    set_pin_light(GREEN_LED_PIN, g, a)
    set_pin_light(BLUE_LED_PIN, b, a)

def set_light_and_brightness_override(rgba_tuple):
    light_effects.kill_effect()
    set_light_and_brightness(rgba_tuple)


def update_clock_thread(): 
    global isDisplayActuallyClear
    while True:
        if shouldDisplayBeClear and not isDisplayActuallyClear:
            time.sleep(0.15)
            clockDisplay.ShowDoublepoint(False)
            clockDisplay.Clear()
            isDisplayActuallyClear = True
        
        elif not shouldDisplayBeClear:
            isDisplayActuallyClear = False
            clockDisplay.ShowDoublepoint(True)
            clockDisplay.Show(currentlySetFourNumbers)

        time.sleep(0.25)

def clear_clock():
    global shouldDisplayBeClear
    shouldDisplayBeClear = True
    clockDisplay.ShowDoublepoint(False)
    clockDisplay.Clear()
    
def display_four_values(four_value_array):
    global shouldDisplayBeClear, currentlySetFourNumbers
    shouldDisplayBeClear = False
    currentlySetFourNumbers = four_value_array
    if isDisplayActuallyClear: # immediate reaction time
        clockDisplay.ShowDoublepoint(True)
        clockDisplay.Show(four_value_array)

def display_clock_time(anyTime):
    hour = anyTime.hour
    minute = anyTime.minute
    if hour > 12:
        hour -= 12
    fourValues = [ int(hour / 10), hour % 10, int(minute / 10), minute % 10 ]
    display_four_values(fourValues)

def display_and_format_seconds(seconds):
    fourValues = [0,0,0,0]
    if seconds < 0:
        logging.error("Hey, no negative seconds!")
        raise Exception("Negative seconds are not allowed!")
    minutes = int(seconds/60.0)
    hours = int(seconds/60.0/60.0)
    if hours >= 1:
        disp_min = minutes - 60 * hours
        fourValues = [ int(hours / 10), hours % 10, int(disp_min / 10), disp_min % 10 ]
    else:
        disp_sec = seconds - 60 * minutes
        fourValues = [ int(minutes / 10), minutes % 10, int(disp_sec / 10), disp_sec % 10 ]
    display_four_values(fourValues)

def update_output_controller():
    pass