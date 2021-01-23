from global_vars import *
import datetime

hasPerformedDailyRecalculation = False

def bedtime():
    pass

def abort_bedtime_protocol():
    pass

def update_time_state_booleans():
    pass

def activate_bedtime_siren_protocol():
    global isBedtimeSirenProtocolEnabled
    if isBedtimeSirenProtocolEnabled:
        return
    isBedtimeSirenProtocolEnabled = True

def activate_bedtime_countdown():
    global isDisplayingBedtimeCountdown
    if isDisplayingBedtimeCountdown:
        return
    isDisplayingBedtimeCountdown = True
    
def display_bedtime():
    global isDisplayingBedtime
    if isDisplayingBedtime:
        return
    
    isDisplayingBedtime = True

def is_daily_calculation_time():
    timestamp = datetime.datetime.now().time() # Throw away the date information
    start = datetime.time(DAILY_RECALCULATION_HOUR)
    end = datetime.time(DAILY_RECALCULATION_HOUR, 0, 1)
    if start <= timestamp <= end:
        return True
    else:
        return False


def calculate_sunrise_of_tomorrow():
    global hasPerformedDailyRecalculation

    hasPerformedDailyRecalculation = True

def update_bedtime_protocol():
    global hasPerformedDailyRecalculation
    
    update_time_state_booleans()

    if not inSession:
        if isPastBedtime:
            activate_bedtime_siren_protocol()
        elif isWithinBedtimeCountdown:
            activate_bedtime_countdown()
        elif isTimeToDisplayBedtime:
            display_bedtime()
    
    if is_daily_calculation_time():
        hasPerformedDailyRecalculation = False
    elif not hasPerformedDailyRecalculation:
        calculate_sunrise_of_tomorrow() 

     