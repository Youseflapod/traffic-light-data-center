from global_vars import * # pylint: disable=unused-wildcard-import
from output_controller import * # pylint: disable=unused-wildcard-import
import logging
from killable_thread import thread_with_trace

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

def fade(startRGBA, endRGBA, time):
    pass

def run_light_thread(effect):
    global isLightEffectRunning

    if effect == END_SESSION:
        set_light_and_brightness((0,0,0,0))

    elif effect == START_SPRINT:
        set_light_and_brightness(SPRINT_L_B)

    elif effect == START_BREAK:
        set_light_and_brightness(BREAK_L_B)

    elif effect == START_INTERRUPTION:
        set_light_and_brightness(INTERRUPTION_L_B)

    elif effect == PAST_BREAK:
        pass
    
    elif effect == ENTERING_OVERTIME:
        pass

    elif effect == PAST_BEDTIME:
        pass

    elif effect == BEDTIME:
        pass

    elif effect == MORNING:
        pass

    elif effect == ABORT_BEDTIME_PROTOCOL:
        pass

    elif effect == BEDTIME_COUNTDOWN:
        set_light_and_brightness((255, 0, 0, 0.5))

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
    set_light_and_brightness((0,0,0,0))
    isLightEffectRunning = False

def start(effect):
    global isLightEffectRunning, light_thread, currentEffect
    currentEffect = effect

    if isLightEffectRunning:
        kill_effect()
        
    isLightEffectRunning = True
    light_thread.start()


def update_light_effects():
    pass