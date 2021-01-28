import constant_parameters as c
import logging
import light_effects
import RPi.GPIO # pylint: disable=import-error
import pigpio # pylint: disable=import-error
from pincfg import *  # pylint: disable=unused-wildcard-import
import tm1637
import time
import datetime
import threading
import bedtime_protocol as bp

pi = pigpio.pi()

PWM_RANGE = 2000
PWM_FREQUENCY = 100
pi.set_PWM_frequency(RED_LED_PIN,PWM_FREQUENCY)
pi.set_PWM_frequency(GREEN_LED_PIN,PWM_FREQUENCY)
pi.set_PWM_frequency(BLUE_LED_PIN,PWM_FREQUENCY)

MAX_GREEN = 120
MAX_BLUE = MAX_GREEN * 0.8

pi.set_PWM_range(RED_LED_PIN, PWM_RANGE)
pi.set_PWM_range(GREEN_LED_PIN, PWM_RANGE)
pi.set_PWM_range(BLUE_LED_PIN, PWM_RANGE)

clockDisplay = tm1637.TM1637(CLK_PIN, DIO_PIN, tm1637.BRIGHT_TYPICAL)
clockDisplay.Clear()
clockDisplay.SetBrightness(c.CLOCK_BRIGHTNESS)

shouldDisplayBeClear = True
isDisplayActuallyClear = True
currentlySetFourNumbers = [0,0,0,0]
currentlyDisplayedLight = (0,0,0,0)

doublePoint = False

def get_currently_displayed_light():
    return currentlyDisplayedLight

def set_pin_light(pin, value, brightness):
    if value > 255 or brightness > 1:
        logging.error(f'Too bright!! My eyes! Can\'t set pin {pin} to {value} with brightness {brightness}')
        raise Exception(f'Too bright!! My eyes! Can\'t set pin {pin} to {value} with brightness {brightness}')
    if value < 0 or brightness < 0:
        logging.error(f'Too dim!! My eyes? Can\'t set pin {pin} to {value} with brightness {brightness}')
        raise Exception(f'Too dim!! My eyes? Can\'t set pin {pin} to {value} with brightness {brightness}')
    realBrightness = int(round(PWM_RANGE * (value * float(brightness)) / 255.0))
    pi.set_PWM_dutycycle(pin, realBrightness)

def calculate_calib_rgba(rgba_tuple):
    r,g,b,a = rgba_tuple
    g = g * MAX_GREEN/255.0
    b = b * MAX_BLUE/255.0
    return (r,g,b,a)

def set_light_rgba(rgba_tuple):
    global currentlyDisplayedLight
    r,g,b,a = rgba_tuple
    currentlyDisplayedLight = rgba_tuple
    set_pin_light(RED_LED_PIN, r, a)
    set_pin_light(GREEN_LED_PIN, g, a)
    set_pin_light(BLUE_LED_PIN, b, a)

def set_light_calib_rgba(rgba_tuple):
    set_light_rgba(calculate_calib_rgba(rgba_tuple))

def override_light_calib_rgba(rgba_tuple):
    light_effects.kill_effect()
    set_light_rgba(rgba_tuple)


def update_clock_thread(): 
    global isDisplayActuallyClear
    while True:
        starttime = time.time()
        if shouldDisplayBeClear and not isDisplayActuallyClear:
            time.sleep(0.15)
            clockDisplay.ShowDoublepoint(doublePoint)
            clockDisplay.Clear()
            isDisplayActuallyClear = True
        
        elif not shouldDisplayBeClear:
            isDisplayActuallyClear = False
            clockDisplay.ShowDoublepoint(doublePoint)
            clockDisplay.Show(currentlySetFourNumbers)

        sleeptime = 0.25 - (time.time() - starttime)
        if sleeptime > 0:
            time.sleep(sleeptime)

def __start_clock_thread():
    t = threading.Thread(target=update_clock_thread, args=[])
    t.start()

__start_clock_thread()

def set_clock_brightness(val):
    # VALUES FROM 0 TO 7
    clockDisplay.SetBrightness(val)

def set_double_point(boolean):
    global doublePoint
    clockDisplay.ShowDoublepoint(boolean)
    doublePoint = boolean

def clear_clock():
    global shouldDisplayBeClear, doublePoint
    shouldDisplayBeClear = True
    
    clockDisplay.Clear()
    
def display_four_values(four_value_array):
    global shouldDisplayBeClear, currentlySetFourNumbers
    shouldDisplayBeClear = False
    currentlySetFourNumbers = four_value_array
    if isDisplayActuallyClear: # immediate reaction time
        clockDisplay.Show(four_value_array)

def display_clock_time(anyTime, fixBrightness = True):
    if fixBrightness:
        set_clock_brightness(c.CLOCK_BRIGHTNESS)
    hour = anyTime.hour
    minute = anyTime.minute
    if hour > 12:
        hour -= 12
    fourValues = [ int(hour / 10), hour % 10, int(minute / 10), minute % 10 ]
    display_four_values(fourValues)
    set_double_point(True)

def display_current_time(fixBrightness = True):
    if fixBrightness:
        set_clock_brightness(c.CLOCK_BRIGHTNESS)
    display_clock_time(bp.get_localized_time().time(), fixBrightness= fixBrightness)

def display_and_format_seconds(seconds, fixBrightness = True):
    if fixBrightness:
        set_clock_brightness(c.CLOCK_BRIGHTNESS)
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
        fourValues = [ int(minutes / 10), int(minutes % 10), int(disp_sec / 10), int(disp_sec % 10) ]
    display_four_values(fourValues)
    set_double_point(True)

def display_and_format_seconds_into_minutes(seconds, fixBrightness = True):
    if fixBrightness:
        set_clock_brightness(c.CLOCK_BRIGHTNESS)
    minutes = int(seconds/60)
    display_and_format_seconds(minutes*60)

def display_int(val, fixBrightness = True):
    if fixBrightness:
        set_clock_brightness(c.CLOCK_BRIGHTNESS)
    if val > 9999:
        logging.error("Can't display a number that big!")
        raise Exception("Can't display a number that big")
    elif val < 0:
        logging.error("Hey, no negative integers!")
        raise Exception("Negative integers are not allowed!")
    #fourValues = [ int(val/1000), int(val/100), int(val/10), int(val % 10)]
    dig = [int(d) for d in str(val)]
    fourValues = [0,0,0,0]
    if val < 10:
        fourValues = [0,0,0,dig[0]]
    elif val < 100:
        fourValues = [0,0,dig[0],dig[1]]  
    elif val < 1000:
        fourValues = [0,dig[0],dig[1],dig[2]]  
    else:
        fourValues = dig
    display_four_values(fourValues)
    set_double_point(False)

def update_output_controller():
    pass