from global_vars import *

def bedtime():
    print()


def abort_bedtime_protocol():
    print()


def update_bedtime_protocol():
    global isBedtimeSirenProtocolEnabled, isDisplayingBedtimeCountdown, isDisplayingBedtime
    update_time_state_booleans()

    if not inSession:
        if isPastBedtime and not isBedtimeSirenProtocolEnabled:
            isBedtimeSirenProtocolEnabled = True
        elif isWithinBedtimeCountdown:
            isDisplayingBedtimeCountdown = True
        elif isTimeToDisplayBedtime:
            isDisplayingBedtime = True
    
    if not hasPerformedDailyRecalculation:
        recalculate_sunrise_tomorrow()