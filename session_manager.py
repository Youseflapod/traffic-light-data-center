import constant_parameters as c
import time
import output_controller as oc # pylint: disable=unused-wildcard-import
import light_effects as leff
import bedtime_protocol as bp
import threading

SESSION = 0
SPRINT = 1
BREAK = 2
INTERRUPTION = 3

inSession = False
inInterruption = False
inBreak = False
inSprint = False
inOverTime = False
isPastBreakTime = False

isDislayingStats = False

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
        oc.override_light_calib_rgba(c.BREAK_L_B)
    if inSprint:
        oc.override_light_calib_rgba(c.SPRINT_L_B)
    else:
        oc.override_light_calib_rgba((0,0,0,0))

def just_passed_break_time():
    global isPastBreakTime
    isPastBreakTime = True

def entering_overtime(): 
    global inOverTime
    inOverTime = True


def __display_stats_thread():
    global isDislayingStats
    isDislayingStats = True
    actualLength = time.time() - startTimes[SPRINT]
    percentFocus = 100.0 * (1 - (interruptionDelay / actualLength) )
    reset_delay()
    oc.display_int(int(round(percentFocus)))
    time.sleep(c.END_STATS_DISPLAY_LENGTH)
    oc.clear_clock()
    isDislayingStats = False


def end_break():
    global inBreak
    inBreak = False
    if inInterruption:
        end_interruption()
    reset_delay()

def end_sprint():
    global inSprint 
    inSprint = False
    if inInterruption:
        end_interruption()

    t = threading.Thread(target=__display_stats_thread, args=[])
    t.start()


def start_break(breakLength):
    global inBreak, startTimes, objectiveTimes
    if inBreak and not inInterruption:
        end_break()
    inBreak = True

    if inSprint:
        end_sprint()

    if inInterruption:
        end_interruption()
    else: 
        startTimes[BREAK] = time.time()
        objectiveTimes[BREAK] = startTimes[BREAK] + breakLength

    leff.start(leff.START_BREAK)
    

def start_sprint(sprintLength):
    global inSprint, startTimes, objectiveTimes 
    if inSprint and not inInterruption:
        end_sprint()
    inSprint = True

    if not inSession:
        start_session()
    if inBreak:
        end_break()

    if inInterruption:
        end_interruption()
    else: 
        time.sleep(0.0085) # in case thread taking time to boot
        startTimes[SPRINT] = time.time()
        objectiveTimes[SPRINT] = startTimes[SPRINT] + sprintLength

    leff.start(leff.START_SPRINT)


def __end_session_thread():
    global inSession
    leff.start(leff.END_SESSION)
    time.sleep(10)
    inSession = False
    oc.clear_clock()
    bp.isDisplayingBedtime = False
    bp.isDisplayingBedtimeCountdown = False
    bp.isBedtimeSirenProtocolEnabled = False

def end_session():
    if inInterruption:
        end_interruption()
    if inSprint:
        end_sprint()
    if inBreak:
        end_break()
    t = threading.Thread(target=__end_session_thread, args=[])
    t.start()


def update_session_manager():
    currentTime = time.time()

    if isDislayingStats:
        return # YOU SHALL NOT PASS

    if inSprint:
        if not inOverTime:
            if not inInterruption:
                oc.display_and_format_seconds(objectiveTimes[SPRINT] + interruptionDelay - currentTime)

            if currentTime > (objectiveTimes[SPRINT] + interruptionDelay):
                entering_overtime()
        else:
            if not inInterruption:
                oc.display_and_format_seconds(currentTime - (objectiveTimes[SPRINT] + interruptionDelay))

    if inBreak: 
        if not isPastBreakTime: 
            if not inInterruption:
                oc.display_and_format_seconds(objectiveTimes[BREAK] + interruptionDelay - currentTime)

            if currentTime > (objectiveTimes[BREAK] + interruptionDelay):
                just_passed_break_time()
        else: 
            if not inInterruption:
                oc.display_and_format_seconds(currentTime - (objectiveTimes[SPRINT] + interruptionDelay))


    if inInterruption:
        oc.display_and_format_seconds(currentTime - startTimes[INTERRUPTION])
