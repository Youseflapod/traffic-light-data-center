from global_vars import *
from output_controller import *
from killable_thread import thread_with_trace

END_SESSION = 0
START_SPRINT = 1
START_BREAK = 2
START_INTERRUPTION = 3
PAST_BREAK = 4
ENTERING_OVERTIME = 5
PAST_BEDTIME = 6
MORNING = 7

currentEffect = -1

def run_light_thread(effect):
    global isLightEffectRunning

    if effect == END_SESSION:
        set_light_and_brightness((0,0,0,0))

    if effect == START_SPRINT:
        set_light_and_brightness(SPRINT_L_B)

    if effect == START_BREAK:
        set_light_and_brightness(BREAK_L_B)

    if effect == START_INTERRUPTION:
        set_light_and_brightness(INTERRUPTION_L_B)

    if effect == PAST_BREAK:
        pass
    
    if effect == ENTERING_OVERTIME:
        pass

    if effect == PAST_BEDTIME:
        pass

    if effect == MORNING:
        pass

    isLightEffectRunning = False

light_thread = thread_with_trace(target= run_light_thread)

def kill_effect():
    global light_thread, isLightEffectRunning
    light_thread.kill() 
    light_thread.join()
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




'''class Effects(object):

    def end_session():
        set_light_and_brightness((0,0,0,0))

    def start_sprint():
        set_light_and_brightness(SPRINT_L_B)

    def start_break():
        set_light_and_brightness(BREAK_L_B)

    def start_interruption():
        set_light_and_brightness(INTERRUPTION_L_B)

    def past_break():
        pass

    def entering_overtime():
        pass

    def past_bedtime():
        pass

    def morning():
        pass'''
