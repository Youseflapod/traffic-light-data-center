import constant_parameters as c
import datetime
from datetime import timedelta
import time
import light_effects as leff
from astral.sun import sun
import output_controller as oc
import threading
import session_manager

isWakeUpTime = False
isCalculatingTime = False

isTimeToDisplayBedtime = False
isWithinBedtimeCountdown = False
isPastBedtime = False
isWakeUpTime = False
isMorningClockTime = False
isInWakeUpPeriod = False
hasWokeUp = False

isDisplayingBedtime = False
isDisplayingBedtimeCountdown = False
isBedtimeSirenProtocolEnabled = False
isDisplayingWakeUp = False

sunriseTomorrow = datetime.datetime.now()
bedtimeTonight = datetime.datetime.now()
wakeTimeTomorrow = datetime.datetime.now()
wakeClockTimeTomorrow = datetime.datetime.now()

showBedtimeTime = datetime.datetime.now()
showBedtimeCountdownTime = datetime.datetime.now()

recordedAbortTime = abortBedtimeDate = datetime.datetime(2000, 1, 1)

recordedBedtime = bedtimeDate = datetime.datetime(2000, 1, 1)


def get_localized_time():
    return c.TZ.localize(datetime.datetime.now())

#__debugWakeTime = get_localized_time()+timedelta(seconds=30)


def dim_clock_to_sleep():
    currentBrightness = 7
    oc.display_clock_time(wakeTimeTomorrow)
    while currentBrightness >= 0:
        oc.clockDisplay.SetBrightness(currentBrightness)
        time.sleep(0.8)
        currentBrightness -= 1
    oc.clear_clock()
    oc.clockDisplay.SetBrightness(c.CLOCK_BRIGHTNESS)

def flash_bedtime_then_sleep():
    currentBrightness = 7
    dim = 1
    oc.display_clock_time(wakeTimeTomorrow)
    time.sleep(9.0)
    intv = 0.5
    for i in range(0,3): 
        oc.clockDisplay.SetBrightness(dim)
        time.sleep(intv)
        oc.clockDisplay.SetBrightness(currentBrightness)
        time.sleep(intv)
    oc.clear_clock()
    oc.set_clock_brightness(c.CLOCK_BRIGHTNESS)

def bedtime():
    global recordedBedtime, bedtimeDate
    global isDisplayingBedtime, isDisplayingBedtimeCountdown, isBedtimeSirenProtocolEnabled
    isDisplayingBedtime = isDisplayingBedtimeCountdown = isBedtimeSirenProtocolEnabled = False
    recordedBedtime = get_localized_time()
    
    bedtimeDate = bedtimeTonight.date()
    
    leff.start(leff.BEDTIME)
    t = threading.Thread(target=flash_bedtime_then_sleep, args=[])
    t.start()

def abort_bedtime_protocol():
    global recordedAbortTime, abortBedtimeDate
    global isDisplayingBedtime, isDisplayingBedtimeCountdown, isBedtimeSirenProtocolEnabled
    isDisplayingBedtime = isDisplayingBedtimeCountdown = isBedtimeSirenProtocolEnabled = False
    recordedAbortTime = get_localized_time()
    
    abortBedtimeDate = bedtimeTonight.date()

    leff.start(leff.ABORT_BEDTIME_PROTOCOL)
    oc.clear_clock()
    oc.set_clock_brightness(c.CLOCK_BRIGHTNESS)

def activate_bedtime_siren_protocol():
    global isBedtimeSirenProtocolEnabled
    dt = get_localized_time() - bedtimeTonight
    oc.display_and_format_seconds_into_minutes(dt.seconds)

    if isBedtimeSirenProtocolEnabled:
        return
    isBedtimeSirenProtocolEnabled = True
    leff.start(leff.PAST_BEDTIME)

def activate_bedtime_countdown():
    global isDisplayingBedtimeCountdown
    dt = bedtimeTonight - get_localized_time()
    oc.display_and_format_seconds(dt.seconds)

    if isDisplayingBedtimeCountdown:
        return
    isDisplayingBedtimeCountdown = True
    leff.start(leff.BEDTIME_COUNTDOWN)
    
def display_bedtime():
    global isDisplayingBedtime
    oc.display_clock_time(bedtimeTonight)
    
    if isDisplayingBedtime:
        return
    isDisplayingBedtime = True

def display_morning_clock():
    global isInWakeUpPeriod
    oc.set_clock_brightness(c.MORNING_CLOCK_BRIGHTNESS)
    oc.display_current_time(fixBrightness=False)
    isInWakeUpPeriod = True

def kill_wake_up():
    global hasWokeUp,isDisplayingWakeUp, isInWakeUpPeriod
    if hasWokeUp:
        return
    hasWokeUp = True
    isDisplayingWakeUp = False
    isInWakeUpPeriod = False

def display_wake_up():
    global isDisplayingWakeUp, isInWakeUpPeriod
    dt = get_localized_time() - wakeTimeTomorrow
    oc.display_and_format_seconds(dt.seconds)
    if dt > c.MORNING_WAKE_PERIOD_MAX_LENGTH:
        kill_wake_up()
    if isDisplayingWakeUp:
        return
    isDisplayingWakeUp = True
    isInWakeUpPeriod = True

def __woke_up_thread(displayFunction, funcInput):
    global isInWakeUpPeriod

    pause = 1.3
    intv = 2
    oc.clear_clock()
    
    for i in range(2):
        time.sleep(pause)
        displayFunction(funcInput)
        time.sleep(intv)
        oc.clear_clock()

    isInWakeUpPeriod = False

def woke_up():
    global hasWokeUp, isDisplayingWakeUp
    if hasWokeUp:
        return
    hasWokeUp = True
    isDisplayingWakeUp = False
    now = get_localized_time()
    dt = get_localized_time() - wakeTimeTomorrow
    alarmlessWakeTime = wakeTimeTomorrow + timedelta(seconds = c.MORNING_FORGOT_TO_HIT_BUTTON_GRACE_PERIOD)
    displayFunction = None
    funcInput = None
    if now < alarmlessWakeTime:
        displayFunction = oc.display_int
        funcInput = 100
    else:
        displayFunction = oc.display_and_format_seconds
        funcInput = dt.seconds
    
    if now < wakeTimeTomorrow + c.MORNING_WAKE_EFFECT_LENGTH:
        leff.start(leff.MORNING_CONGRATULATIONS_BIG)
    else:
        leff.start(leff.MORNING_CONGRATULATIONS)
    
    t = threading.Thread(target=__woke_up_thread, args=(displayFunction,funcInput))
    t.start()


def check_if_time_to_update_calculations():
    global isCalculatingTime, hasWokeUp
    start = get_localized_time().replace(hour=c.DAILY_RECALCULATION_TIME.hour, minute=c.DAILY_RECALCULATION_TIME.minute)
    end = start + timedelta(seconds=20)
    if start <= get_localized_time() <= end:
        if isCalculatingTime:
            return
        isCalculatingTime = True
        calculate_sunrise_of_tomorrow_and_bedtime() 
        hasWokeUp = False
    else:
        isCalculatingTime = False

def update_time_state_booleans():
    global isTimeToDisplayBedtime, isWithinBedtimeCountdown, isPastBedtime
    global isWakeUpTime, isMorningClockTime
    now = get_localized_time()

    isTimeToDisplayBedtime = isWithinBedtimeCountdown = isPastBedtime = False 
    isWakeUpTime = isMorningClockTime = False

    wakeTimeEnd = wakeTimeTomorrow + timedelta(seconds=c.MORNING_WAKE_EFFECT_LENGTH)
    if wakeTimeTomorrow < now < wakeTimeEnd:
        isWakeUpTime = True

    morningClockStart = wakeTimeTomorrow - timedelta(seconds=c.MORNING_CLOCK_TIME_LENGTH)
    if morningClockStart < now < wakeTimeTomorrow:
        isMorningClockTime = True

    if showBedtimeTime < now < showBedtimeCountdownTime:
        isTimeToDisplayBedtime = True
    elif showBedtimeCountdownTime < now < bedtimeTonight:
        isWithinBedtimeCountdown = True
    elif now > bedtimeTonight:
        isPastBedtime = True

def should_bedtime_protocol_continue():
    if abortBedtimeDate.day == bedtimeTonight.day:
        return False
    if bedtimeDate.day == bedtimeTonight.day:
        return False
    else:
        return True

def calculate_sunrise_of_tomorrow_and_bedtime():
    global sunriseTomorrow, bedtimeTonight, wakeTimeTomorrow,wakeClockTimeTomorrow
    global showBedtimeTime, showBedtimeCountdownTime
    tomorrow = get_localized_time() + timedelta(days=1)
    if get_localized_time() < get_localized_time().replace(hour=c.DAILY_RECALCULATION_TIME.hour, minute=c.DAILY_RECALCULATION_TIME.minute):
        tomorrow = get_localized_time()
    s = sun(c.CITY.observer, date=tomorrow.date(), tzinfo=c.CITY.timezone)
    sunriseTomorrow = s["sunrise"]
    sunriseTomorrow = sunriseTomorrow.replace(second=0) # keep things fair 
    bedtimeTonight = sunriseTomorrow - timedelta(seconds=c.CALCULATED_BEDTIME_BEFORE_SUNRISE)
    wakeTimeTomorrow = sunriseTomorrow - timedelta(seconds=c.CALCULATED_WAKE_TIME_BEFORE_SUNRISE)
    wakeClockTimeTomorrow = wakeTimeTomorrow - timedelta(seconds=c.MORNING_CLOCK_TIME_LENGTH)
    showBedtimeCountdownTime = bedtimeTonight - timedelta(seconds=c.BEDTIME_COUNTDOWN_LENGTH)
    showBedtimeTime = bedtimeTonight - timedelta(seconds=c.DISPLAY_BEDTIME_LENGTH)
    print(bedtimeTonight)
    print(wakeTimeTomorrow)

'''def check_if_wake_up_time():
    global isWakeUpTime
    start = wakeTimeTomorrow
    end = start + timedelta(seconds=5)
    if start <= get_localized_time() <= end:
        if isWakeUpTime:
            return
        isWakeUpTime = True
        leff.start(leff.MORNING)
    else:
        isWakeUpTime = False'''

def update_bedtime_protocol():
    update_time_state_booleans()

    if not session_manager.inSession:
        if not hasWokeUp:
            if isWakeUpTime:
                display_wake_up()
            elif isMorningClockTime:
                display_morning_clock()

        if should_bedtime_protocol_continue():
            if isPastBedtime:
                activate_bedtime_siren_protocol()
            elif isWithinBedtimeCountdown:
                activate_bedtime_countdown()
            elif isTimeToDisplayBedtime:
                display_bedtime()
    
    check_if_time_to_update_calculations()
    #check_if_wake_up_time()
