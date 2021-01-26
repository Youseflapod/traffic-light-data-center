import constant_parameters as c 
from output_controller import * # pylint: disable=unused-wildcard-import
import logging
from killable_thread import thread_with_trace
import numpy as np

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

def fade_linear(endRGBA, length):
    startRGBA = get_currently_displayed_light()
    numberOfFrames = int(length / float(SLEEP_TIME))
    differences = tuple(map(lambda i, j: i - j, endRGBA, startRGBA))
    stepSizes = tuple(map(lambda i: float(i) / numberOfFrames, differences))
    set_light_rgba(startRGBA)

    for n in range(1, numberOfFrames+1):
        time.sleep(SLEEP_TIME)
        deltaRGBA = tuple(map(lambda i: i * n, stepSizes))
        currentRGBA = tuple(map(lambda i, j: i + j, startRGBA, deltaRGBA))
        set_light_rgba(currentRGBA)


def fade_off(length):
    red,green,blue,alpha = get_currently_displayed_light()
    numberOfFrames = int(length / float(SLEEP_TIME))
    T = float(length)
    b = EXP_FINAL_SLOPE
    C = alpha
    a = -1 * (1/T) * np.log(b / (C + b) )
    for n in range(1, numberOfFrames+1):
        time.sleep(SLEEP_TIME)
        t = n * SLEEP_TIME
        currentBrightness = (C + b)*np.exp(-1*a*t) - b
        set_light_rgba((red,green,blue,currentBrightness))

        
def run_light_thread():
    global isLightEffectRunning
    effect = currentEffect

    if effect == END_SESSION:
        set_light_rgba((0,0,0,0))

    elif effect == START_SPRINT:
        set_light_rgba(c.SPRINT_L_B)

    elif effect == START_BREAK:
        set_light_rgba(c.BREAK_L_B)

    elif effect == START_INTERRUPTION:
        set_light_rgba(c.INTERRUPTION_L_B)

    elif effect == PAST_BREAK:
        pass
    
    elif effect == ENTERING_OVERTIME:
        pass

    elif effect == PAST_BEDTIME:
        pass

    elif effect == BEDTIME:
        r,g,b,a = c.BREAK_L_B
        set_light_calib_rgba(r,g,b,1)
        fade_off(10)

    elif effect == MORNING:
        pass

    elif effect == ABORT_BEDTIME_PROTOCOL:
        pass

    elif effect == BEDTIME_COUNTDOWN:
        set_light_rgba((255, 0, 0, 0.5))

    elif effect == DEMO_MODE:
        pass

    else:
        logging.error(f'Oops! No such available effect with the value: {effect}' )
        raise Exception(f'Oops! No such available effect with the value: {effect}')

    isLightEffectRunning = False

light_thread = thread_with_trace(target= run_light_thread)

def kill_effect():
    global light_thread, isLightEffectRunning
    light_thread.kill() 
    light_thread.join()
    set_light_rgba((0,0,0,0))
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