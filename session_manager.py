from global_vars import *
import time
from output_controller import *
import light_effects as leff

SESSION = 0
SPRINT = 1
BREAK = 2
INTERRUPTION = 3

startTimes = [0, 0, 0, 0]
objectiveTimes = [0, 0, 0, 0]

interruptionDelay = 0

def reset_delay():
    global interruptionDelay
    interruptionDelay = 0

def start_session():
    global inSession, startTimes 
    inSession = True
    startTimes[SESSION] = time.time()


def start_interruption():
    global inInterruption, startTimes
    inInterruption = True
    startTimes[INTERRUPTION] = time.time()
    leff.start(leff.START_INTERRUPTION)

def end_interruption():
    global inInterruption, interruptionDelay 
    inInterruption = False
    interruptionDelay += time.time() - startTimes[INTERRUPTION]
   
    if inBreak:
        set_light_and_brightness(BREAK_L_B)
    if inSprint:
        set_light_and_brightness(SPRINT_L_B)

def just_passed_break_time():
    global isPastBreakTime
    isPastBreakTime = True

def entering_overtime(): 
    global inOverTime
    inOverTime = True

def end_break():
    global inBreak
    inBreak = False
    reset_delay()

def end_sprint():
    global inSprint 
    inSprint = False
    reset_delay()


def start_break(breakLength):
    global inBreak, startTimes, objectiveTimes
    startTimes[BREAK] = time.time()
    objectiveTimes[BREAK] = startTimes[BREAK] + breakLength
    inBreak = True

    if inInterruption:
        end_interruption()
    if inSprint:
        end_sprint()

    leff.start(leff.START_BREAK)
    

def start_sprint(sprintLength):
    global inSprint, startTimes, objectiveTimes 
    inSprint = True
    startTimes[SPRINT] = time.time()
    objectiveTimes[SPRINT] = startTimes[SPRINT] + sprintLength

    if not inSession:
        start_session()
    if inBreak:
        end_break()
    if inInterruption:
        end_interruption()

    leff.start(leff.START_SPRINT)


def end_session():
    global inSession
    inSession = False
    if inInterruption:
        end_interruption()
    if inSprint:
        end_sprint()
    if inBreak:
        end_break()

    leff.start(leff.END_SESSION)


def update_session_manager():
    global inOverTime, isPastBreakTime 
    currentTime = time.time()

    if inSprint:
        if not inOverTime:
            if not inInterruption:
                display_min_and_sec(objectiveTimes[SPRINT] + interruptionDelay - currentTime)

            if currentTime > (objectiveTimes[SPRINT] + interruptionDelay):
                entering_overtime()
        else:
            if not inInterruption:
                display_min_and_sec(currentTime - (objectiveTimes[SPRINT] + interruptionDelay))

    if inBreak: 
        if not isPastBreakTime: 
            if not inInterruption:
                display_min_and_sec(objectiveTimes[BREAK] + interruptionDelay - currentTime)

            if currentTime > (objectiveTimes[BREAK] + interruptionDelay):
                just_passed_break_time()
        else: 
            if not inInterruption:
                display_min_and_sec(currentTime - (objectiveTimes[SPRINT] + interruptionDelay))


    if inInterruption:
        display_min_and_sec(currentTime - startTimes[INTERRUPTION])