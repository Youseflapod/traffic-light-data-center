import constant_parameters as c 
import output_controller as oc
import logging
from killable_thread import thread_with_trace
import numpy as np
from time import sleep
import time

END_SESSION = 0
START_SPRINT = 1
START_BREAK = 2
START_INTERRUPTION = 3
PAST_BREAK = 4
ENTERING_OVERTIME = 5
PAST_BEDTIME = 6
BEDTIME = 7
MORNING = 8
ABORT_BEDTIME_PROTOCOL = 9
BEDTIME_COUNTDOWN = 10
DEMO_MODE = 11

currentEffect = -1
isLightEffectRunning = False

FADE_FPS = 144
SLEEP_TIME = 1.0 / FADE_FPS
EXP_FINAL_SLOPE = 0.025
COMPUTE_TIME = 0.0016025641025641

def turnOff():
    oc.set_light_rgba((0,0,0,0))

def fade_linear(endRGBA, length): # DOES NOT USE CALIB
    startRGBA = oc.get_currently_displayed_light()
    numberOfFrames = int(length / float(SLEEP_TIME))
    differences = tuple(map(lambda i, j: i - j, endRGBA, startRGBA))
    stepSizes = tuple(map(lambda i: float(i) / numberOfFrames, differences))
    oc.set_light_rgba(startRGBA)

    for n in range(1, numberOfFrames+1):
        time.sleep(SLEEP_TIME - COMPUTE_TIME)
        deltaRGBA = tuple(map(lambda i: i * n, stepSizes))
        currentRGBA = tuple(map(lambda i, j: i + j, startRGBA, deltaRGBA))
        oc.set_light_rgba(currentRGBA)


def fade_off(length):
    red,green,blue,alpha = oc.get_currently_displayed_light()
    numberOfFrames = int(length / float(SLEEP_TIME))
    T = float(length)
    b = EXP_FINAL_SLOPE
    C = alpha
    a = -1 * (1/T) * np.log(b / (C + b) )
    for n in range(1, numberOfFrames+1):
        time.sleep(SLEEP_TIME - COMPUTE_TIME)
        t = n * SLEEP_TIME
        currentBrightness = (C + b)*np.exp(-1*a*t) - b
        oc.set_light_rgba((red,green,blue,currentBrightness))
    turnOff()

def fade_on(endRGBA,length):
    red,green,blue,alpha = endRGBA
    numberOfFrames = int(length / float(SLEEP_TIME))
    T = float(length)
    b = EXP_FINAL_SLOPE
    C = alpha
    a = -1 * (1/T) * np.log(b / (C + b) )
    for n in range(1, numberOfFrames+1):
        time.sleep(SLEEP_TIME - COMPUTE_TIME)
        t = n * SLEEP_TIME
        currentBrightness = (C + b)*np.exp(-1*a*(T-t)) - b
        oc.set_light_calib_rgba((red,green,blue,currentBrightness))

        
def run_light_thread():
    from output_controller import set_light_rgba, set_light_calib_rgba
    global isLightEffectRunning
    effect = currentEffect

    if effect == END_SESSION:
        fade_linear((255,0,120,1), 2)
        fade_off(4)

    elif effect == START_SPRINT:
        set_light_calib_rgba(c.SPRINT_L_B)

    elif effect == START_BREAK:
        fade_on(c.BREAK_L_B, 4)
        #set_light_rgba(c.BREAK_L_B)

    elif effect == START_INTERRUPTION:
        intv = 0.2 # s
        flash = 0.07
        flashPause = 0.05
        for i in range(0,3):
            fade_off(flash)
            sleep(intv)
            fade_on(c.INTERRUPTION_L_B,flash)
            sleep(flashPause)

        intv = 1.5 # s
        while effect == START_INTERRUPTION:
            set_light_calib_rgba(c.INTERRUPTION_L_B)
            sleep(intv)
            turnOff()
            sleep(intv)

    elif effect == PAST_BREAK:
        intv = 0.55 # s
        pause = 1.2
        r,g,b,a = c.BREAK_L_B # pylint: disable=unused-variable
        while effect == PAST_BREAK:
            fade_on((r,g,b,1), intv)
            sleep(pause)
            fade_off(intv)
            sleep(pause)
    
    elif effect == ENTERING_OVERTIME:
        intv = 0.17 # s
        flash = 0.15
        flashPause = 0.13
        turnOff()
        sleep(0.22)
        for i in range(0,2):
            set_light_rgba((0,255,0,1))
            sleep(flashPause)
            fade_off(flash)
            sleep(intv)
        fade_on(c.SPRINT_L_B, 1.4)    
        

    elif effect == PAST_BEDTIME:
        intv = 0.18 # s
        cooldown = 2.1
        while effect == PAST_BEDTIME:
            set_light_calib_rgba(c.INTERRUPTION_L_B)
            sleep(intv)
            fade_off(cooldown)
            sleep(intv)

    elif effect == BEDTIME:
        r,g,b,a = c.BREAK_L_B # pylint: disable=unused-variable
        set_light_calib_rgba((r,g,b, 1))
        fade_off(8.3)

    elif effect == MORNING:
        intv = 5 # s
        #drop = 0.3 # s
        pause = 5
        startTime = time.time()
        endTime = startTime + c.MORNING_WAKE_EFFECT_LENGTH
        while time.time() < endTime:
            fade_on(c.MORNING_L_B, intv)
            sleep(pause)
            fade_off(intv)
            sleep(pause)

    elif effect == ABORT_BEDTIME_PROTOCOL:
        intv = 0.3 # s
        for i in range(0,5):
            turnOff()
            sleep(intv)
            set_light_calib_rgba(c.INTERRUPTION_L_B)
            sleep(intv)
        fade_off(2.3)

    elif effect == BEDTIME_COUNTDOWN:
        intv = 0.5 # s
        longBoot = 3. # s
        fade_on((255, 9, 0, 0.2), intv)    
        fade_off(intv)
        fade_on((255, 9, 0, 0.2), intv)
        fade_off(intv)
        
        fade_on((255, 40, 0, 0.2), longBoot)

    elif effect == DEMO_MODE:
        intv = 0.08 # s
        for i in range(0,10):
            set_light_rgba((255,255,255,1))
            sleep(intv)
            turnOff()
            sleep(intv)
        intv = 0.3# s
        for i in range(0,12):
            set_light_rgba((255,0,0,1))
            sleep(0.05)
            fade_linear((255,200,0,1),intv)
            fade_linear((0,255,0,1),intv)
            fade_linear((0,0,255,1),intv)
        fade_linear((255,0,120,1), 2)
        fade_off(7)

    else:
        logging.error(f'Oops! No such available effect with the value: {effect}' )
        raise Exception(f'Oops! No such available effect with the value: {effect}')

    isLightEffectRunning = False

light_thread = thread_with_trace(target= run_light_thread)

def kill_effect():
    global light_thread, isLightEffectRunning
    light_thread.kill() 
    light_thread.join()
    oc.set_light_rgba((0,0,0,0))
    isLightEffectRunning = False

def start(effect):
    global isLightEffectRunning, light_thread, currentEffect
    currentEffect = effect

    if isLightEffectRunning:
        kill_effect()
        
    isLightEffectRunning = True
    light_thread = thread_with_trace(target= run_light_thread)
    light_thread.start()


def update_light_effects():
    pass