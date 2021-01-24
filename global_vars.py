from constant_parameters import * # pylint: disable=unused-wildcard-import

inSession = False
inInterruption = False
inBreak = False
inSprint = False
inOverTime = False
isPastBreakTime = False

isLightEffectRunning = False

isTimeToDisplayBedtime = False
isWithinBedtimeCountdown = False
isPastBedtime = False
isDisplayingBedtime = False
isDisplayingBedtimeCountdown = False
isBedtimeSirenProtocolEnabled = False

sunriseTomorrow = datetime.datetime.now()
bedtimeTonight = datetime.datetime.now()
wakeTimeTomorrow = datetime.datetime.now()