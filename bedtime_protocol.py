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


def get_localized_time():
    return c.TZ.localize(datetime.datetime.now())

__debugWakeTime = get_localized_time()+timedelta(seconds=30)


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
    if isPastBedtime and bedtimeTonight.day != recordedBedtime.day:
        # shame on you
        bedtimeDate = bedtimeTonight.date()
    else:
        bedtimeDate = get_localized_time().date()
    leff.start(leff.BEDTIME)
    t = threading.Thread(target=flash_bedtime_then_sleep, args=[])
    t.start()

def abort_bedtime_protocol():
    global recordedAbortTime, abortBedtimeDate
    global isDisplayingBedtime, isDisplayingBedtimeCountdown, isBedtimeSirenProtocolEnabled
    isDisplayingBedtime = isDisplayingBedtimeCountdown = isBedtimeSirenProtocolEnabled = False
    recordedAbortTime = get_localized_time()
    if isPastBedtime and bedtimeTonight.day != recordedAbortTime.day:
        # shame on you
        abortBedtimeDate = bedtimeTonight.date()
    else:
        abortBedtimeDate = get_localized_time().date()

    leff.start(leff.ABORT_BEDTIME_PROTOCOL)
    oc.clear_clock()
    oc.set_clock_brightness(c.CLOCK_BRIGHTNESS)

def activate_bedtime_siren_protocol():
    global isBedtimeSirenProtocolEnabled
    dt = get_localized_time() - bedtimeTonight
    oc.display_and_format_seconds(int(dt.seconds/60.0))

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

def check_if_time_to_update_calculations():
    global isCalculatingTime
    start = get_localized_time().replace(hour=c.DAILY_RECALCULATION_HOUR)
    end = start + timedelta(seconds=20)
    if start <= get_localized_time() <= end:
        if isCalculatingTime:
            return
        isCalculatingTime = True
        calculate_sunrise_of_tomorrow_and_bedtime() 
    else:
        isCalculatingTime = False

def update_time_state_booleans():
    global isTimeToDisplayBedtime, isWithinBedtimeCountdown, isPastBedtime
    now = get_localized_time()

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
    tomorrow = get_localized_time() + timedelta(days=1)
    if get_localized_time() < get_localized_time().replace(hour=c.DAILY_RECALCULATION_HOUR):
        tomorrow = get_localized_time()
    s = sun(c.CITY.observer, date=tomorrow.date(), tzinfo=c.CITY.timezone)
    hasPerformedDailyRecalculation = True
    sunriseTomorrow = s["sunrise"]
    bedtimeTonight = sunriseTomorrow - timedelta(seconds=c.CALCULATED_BEDTIME_BEFORE_SUNRISE)
    wakeTimeTomorrow = sunriseTomorrow - timedelta(seconds=c.CALCULATED_WAKE_TIME_BEFORE_SUNRISE)
    showBedtimeCountdownTime = bedtimeTonight - timedelta(seconds=c.BEDTIME_COUNTDOWN_LENGTH)
    showBedtimeTime = bedtimeTonight - timedelta(seconds=c.DISPLAY_BEDTIME_LENGTH)
    print(bedtimeTonight)
    print(wakeTimeTomorrow)
    print(showBedtimeCountdownTime)
    print(showBedtimeTime)

def check_if_wake_up_time():
    global isWakeUpTime
    start = __debugWakeTime #wakeTimeTomorrow
    end = start + timedelta(seconds=5)
    if start <= get_localized_time() <= end:
        if isWakeUpTime:
            return
        isWakeUpTime = True
        leff.start(leff.MORNING)
    else:
        isWakeUpTime = False

def update_bedtime_protocol():
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
