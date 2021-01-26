from pincfg import * # pylint: disable=unused-wildcard-import
import time
import RPi.GPIO as GPIO # pylint: disable=import-error
import button_logic as bl
import constant_parameters as c
import debug_light_effects

isGreenPressed = isYellowPressed = isRedPressed = False
greenTimeHeld = yellowTimeHeld = redTimeHeld = 0

flickeringTimers = [0.0,0.0,0.0]
startTime = [0.0,0.0,0.0]

def too_long(timeHeld):
    return timeHeld < c.MAX_CLICK_TIME

def green_button_released(timeHeld):
    if not too_long:
        bl.green_button_clicked()

def yellow_button_released(timeHeld):
    if not too_long:
        bl.yellow_button_clicked()

def red_button_released(timeHeld):
    if not too_long:
        bl.red_button_clicked()


def gpio_green_button_pressed(channel):
    global isGreenPressed, startTime
    if not isGreenPressed:
        bl.green_button_just_pressed()
        startTime[GREEN] = time.time()
        isGreenPressed = True
        
def gpio_green_button_released(channel):
    global flickeringTimers
    flickeringTimers[GREEN] = c.FLICKERING_TOLERANCE


def gpio_yellow_button_pressed(channel):
    global isYellowPressed, startTime
    if not isYellowPressed:
        bl.yellow_button_just_pressed()
        startTime[YELLOW] = time.time()
        isYellowPressed = True
        
def gpio_yellow_button_released(channel):
    global flickeringTimers
    flickeringTimers[YELLOW] = c.FLICKERING_TOLERANCE


def gpio_red_button_pressed(channel):
    global isRedPressed, startTime
    if not isRedPressed:
        bl.red_button_just_pressed()
        startTime[RED] = time.time()
        isRedPressed = True
        
def gpio_red_button_released(channel):
    global flickeringTimers
    flickeringTimers[RED] = c.FLICKERING_TOLERANCE


def gpio_green_button_both(channel):
    if GPIO.input(GREEN_BUTTON_PIN) == GPIO.HIGH:
        gpio_green_button_pressed(channel)
    else:
        gpio_green_button_released(channel)

def gpio_yellow_button_both(channel):
    if GPIO.input(YELLOW_BUTTON_PIN) == GPIO.HIGH:
        gpio_yellow_button_pressed(channel)
    else:
        gpio_yellow_button_released(channel)

def gpio_red_button_both(channel):
    if GPIO.input(RED_BUTTON_PIN) == GPIO.HIGH:
        gpio_red_button_pressed(channel)
    else:
        gpio_red_button_released(channel)


if not debug_light_effects.DEBUG:
    GPIO.add_event_detect(GREEN_BUTTON_PIN,GPIO.BOTH,callback=gpio_green_button_both) 
    GPIO.add_event_detect(YELLOW_BUTTON_PIN,GPIO.BOTH,callback=gpio_yellow_button_both) 
    GPIO.add_event_detect(RED_BUTTON_PIN,GPIO.BOTH,callback=gpio_red_button_both) 


def listen_to_the_buttons():
    global flickeringTimers, startTime
    global isGreenPressed, isYellowPressed, isRedPressed
    global greenTimeHeld, yellowTimeHeld, redTimeHeld

    if not GPIO.input(GREEN_BUTTON_PIN) == GPIO.HIGH:
        if isGreenPressed:
            flickeringTimers[GREEN] -= c.DT
            if flickeringTimers[GREEN] <= 0:
                isGreenPressed = False
                green_button_released(greenTimeHeld) 
                
    if isGreenPressed:
        greenTimeHeld = time.time() - startTime[GREEN]



    if not GPIO.input(YELLOW_BUTTON_PIN) == GPIO.HIGH:
        if isYellowPressed:
            flickeringTimers[YELLOW] -= c.DT
            if flickeringTimers[YELLOW] <= 0:
                isYellowPressed = False
                yellow_button_released(yellowTimeHeld) 
                
    if isYellowPressed:
        yellowTimeHeld = time.time() - startTime[YELLOW]
    
    

    if not GPIO.input(RED_BUTTON_PIN) == GPIO.HIGH:
        if isRedPressed:
            flickeringTimers[RED] -= c.DT
            if flickeringTimers[RED] <= 0:
                isRedPressed = False
                red_button_released(redTimeHeld) 
                
    if isRedPressed:
        redTimeHeld = time.time() - startTime[RED]

def isOneButtonPressed():
    if isGreenPressed and isYellowPressed:
        return False
    elif isGreenPressed and isRedPressed:
        return False
    elif isYellowPressed and isRedPressed:
        return False
    else:
        return True