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
isDisplayingBedtime = False
isDisplayingBedtimeCountdown = False
isBedtimeSirenProtocolEnabled = False

sunriseTomorrow = datetime.datetime.now()
bedtimeTonight = datetime.datetime.now()
wakeTimeTomorrow = datetime.datetime.now()

showBedtimeTime = datetime.datetime.now()
showBedtimeCountdownTime = datetime.datetime.now()

recordedAbortTime = abortBedtimeDate = datetime.datetime(2000, 1, 1)

recordedBedtime = bedtimeDate = datetime.datetime(2000, 1, 1)

def dim_clock_to_sleep():
    currentBrightness = 7
    oc.display_clock_time(wakeTimeTomorrow)
    while currentBrightness >= 0:
        oc.clockDisplay.SetBrightness(currentBrightness)
        time.sleep(0.8)
        currentBrightness -= 1
    oc.clear_clock()
    oc.clockDisplay.SetBrightness(c.CLOCK_BRIGHTNESS)

def bedtime():
    global recordedBedtime, bedtimeDate
    global isDisplayingBedtime, isDisplayingBedtimeCountdown, isBedtimeSirenProtocolEnabled
    isDisplayingBedtime = isDisplayingBedtimeCountdown = isBedtimeSirenProtocolEnabled = False
    recordedBedtime = datetime.datetime.now()
    if isPastBedtime and bedtimeTonight.day != recordedBedtime.day:
        # shame on you
        bedtimeDate = bedtimeTonight.date()
    else:
        bedtimeDate = datetime.datetime.today().date()
    leff.start(leff.BEDTIME)
    t = threading.Thread(target=dim_clock_to_sleep, args=[])
    t.start()

def abort_bedtime_protocol():
    global recordedAbortTime, abortBedtimeDate
    global isDisplayingBedtime, isDisplayingBedtimeCountdown, isBedtimeSirenProtocolEnabled
    isDisplayingBedtime = isDisplayingBedtimeCountdown = isBedtimeSirenProtocolEnabled = False
    recordedAbortTime = datetime.datetime.now()
    if isPastBedtime and bedtimeTonight.day != recordedAbortTime.day:
        # shame on you
        abortBedtimeDate = bedtimeTonight.date()
    else:
        abortBedtimeDate = datetime.datetime.today().date()

    leff.start(leff.ABORT_BEDTIME_PROTOCOL)

def activate_bedtime_siren_protocol():
    global isBedtimeSirenProtocolEnabled
    if isBedtimeSirenProtocolEnabled:
        return
    isBedtimeSirenProtocolEnabled = True

    leff.start(leff.PAST_BEDTIME)

def activate_bedtime_countdown():
    global isDisplayingBedtimeCountdown
    if isDisplayingBedtimeCountdown:
        return
    dt = bedtimeTonight - datetime.datetime.now()
    oc.display_and_format_seconds(dt.seconds)
    isDisplayingBedtimeCountdown = True
    leff.start(leff.BEDTIME_COUNTDOWN)
    
def display_bedtime():
    global isDisplayingBedtime
    if isDisplayingBedtime:
        return
    oc.display_clock_time(bedtimeTonight)
    isDisplayingBedtime = True

def check_if_time_to_update_calculations():
    global isCalculatingTime
    start = datetime.time(c.DAILY_RECALCULATION_HOUR)
    end = start + timedelta(seconds=5)
    if start <= datetime.datetime.now() <= end:
        if isCalculatingTime:
            return
        isCalculatingTime = True
        calculate_sunrise_of_tomorrow_and_bedtime() 
    else:
        isCalculatingTime = False

def update_time_state_booleans():
    global isTimeToDisplayBedtime, isWithinBedtimeCountdown, isPastBedtime
    now = datetime.datetime.now()
    if now.day != bedtimeTonight.day:
        return # waiting until next recalculation
    # after midnight, isPastBedtime remains on until further update

    isTimeToDisplayBedtime = isWithinBedtimeCountdown = isPastBedtime = False

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
    global hasPerformedDailyRecalculation, sunriseTomorrow, bedtimeTonight, wakeTimeTomorrow
    global showBedtimeTime, showBedtimeCountdownTime
    tomorrow = datetime.datetime.today() + timedelta(days=1)
    s = sun(c.CITY.observer, date=tomorrow.date(), tzinfo=c.CITY.timezone)
    hasPerformedDailyRecalculation = True
    sunriseTomorrow = s["sunrise"]
    bedtimeTonight = sunriseTomorrow - timedelta(seconds=c.CALCULATED_BEDTIME_BEFORE_SUNRISE)
    wakeTimeTomorrow = sunriseTomorrow - timedelta(seconds=c.CALCULATED_WAKE_TIME_BEFORE_SUNRISE)
    showBedtimeCountdownTime = bedtimeTonight - timedelta(seconds=c.BEDTIME_COUNTDOWN_LENGTH)
    showBedtimeTime = bedtimeTonight - timedelta(seconds=c.DISPLAY_BEDTIME_LENGTH)

def check_if_wake_up_time():
    global isWakeUpTime
    start = wakeTimeTomorrow
    end = start + timedelta(seconds=5)
    if start <= datetime.datetime.now() <= end:
        if isWakeUpTime:
            return
        isWakeUpTime = True
        leff.start(leff.MORNING)
    else:
        isWakeUpTime = False

def update_bedtime_protocol():
    global hasPerformedDailyRecalculation, hasWokeUp
    
    update_time_state_booleans()

    if not session_manager.inSession:
        if should_bedtime_protocol_continue():
            if isPastBedtime:
                activate_bedtime_siren_protocol()
            elif isWithinBedtimeCountdown:
                activate_bedtime_countdown()
            elif isTimeToDisplayBedtime:
                display_bedtime()
    
    check_if_time_to_update_calculations()
    check_if_wake_up_time()
