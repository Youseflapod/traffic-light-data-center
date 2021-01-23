from pincfg import *
import time
import RPi.GPIO as GPIO
import button_logic as bl
from global_vars import *

isGreenPressed = isYellowPressed = isRedPressed = False
greenTimeHeld = yellowTimeHeld = redTimeHeld = 0

flickeringTimers = [0.0,0.0,0.0]
startTime = [0.0,0.0,0.0]

def too_long(timeHeld):
    return timeHeld < MAX_CLICK_TIME

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
    flickeringTimers[GREEN] = FLICKERING_TOLERANCE


def gpio_yellow_button_pressed(channel):
    global isYellowPressed, startTime
    if not isYellowPressed:
        bl.yellow_button_just_pressed()
        startTime[YELLOW] = time.time()
        isYellowPressed = True
        
def gpio_yellow_button_released(channel):
    global flickeringTimers
    flickeringTimers[YELLOW] = FLICKERING_TOLERANCE


def gpio_red_button_pressed(channel):
    global isRedPressed, startTime
    if not isRedPressed:
        bl.red_button_just_pressed()
        startTime[RED] = time.time()
        isRedPressed = True
        
def gpio_red_button_released(channel):
    global flickeringTimers
    flickeringTimers[RED] = FLICKERING_TOLERANCE

GPIO.add_event_detect(GREEN_PIN,GPIO.RISING,callback=gpio_green_button_pressed) 
GPIO.add_event_detect(GREEN_PIN,GPIO.FALLING,callback=gpio_green_button_released)

GPIO.add_event_detect(YELLOW_PIN,GPIO.RISING,callback=gpio_yellow_button_pressed) 
GPIO.add_event_detect(YELLOW_PIN,GPIO.FALLING,callback=gpio_yellow_button_released)

GPIO.add_event_detect(RED_PIN,GPIO.RISING,callback=gpio_red_button_pressed) 
GPIO.add_event_detect(RED_PIN,GPIO.FALLING,callback=gpio_red_button_released)

def listen_to_the_buttons():
    global flickeringTimers, startTime
    global isGreenPressed, isYellowPressed, isRedPressed
    global greenTimeHeld, yellowTimeHeld, redTimeHeld

    if not GPIO.input(GREEN_PIN) == GPIO.HIGH:
        if isGreenPressed:
            flickeringTimers[GREEN] -= DT
            if flickeringTimers[GREEN] <= 0:
                isGreenPressed = False
                green_button_released(greenTimeHeld) 
                
    if isGreenPressed:
        greenTimeHeld = time.time() - startTime[GREEN]



    if not GPIO.input(YELLOW_PIN) == GPIO.HIGH:
        if isYellowPressed:
            flickeringTimers[YELLOW] -= DT
            if flickeringTimers[YELLOW] <= 0:
                isYellowPressed = False
                yellow_button_released(yellowTimeHeld) 
                
    if isYellowPressed:
        yellowTimeHeld = time.time() - startTime[YELLOW]
    
    

    if not GPIO.input(RED_PIN) == GPIO.HIGH:
        if isRedPressed:
            flickeringTimers[RED] -= DT
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