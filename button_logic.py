from global_vars import * # pylint: disable=unused-wildcard-import
from button_listener import * # pylint: disable=unused-wildcard-import
from session_manager import * # pylint: disable=unused-wildcard-import
from bedtime_protocol import * # pylint: disable=unused-wildcard-import
import light_effects as leff

inDemoMode = False

def green_button_clicked():
    start_sprint(STANDARD_SPRINT_LENGTH)
    if inInterruption:
        end_interruption()

def yellow_button_clicked():
    if inSession:
        start_break(STANDARD_BREAK_LENGTH)

def red_button_clicked():
    pass

def green_button_just_pressed():
    pass

def yellow_button_just_pressed():
    pass

def red_button_just_pressed():
    pass
    if inSession:
        start_interruption() # because there is no hold function during session, so more immediate

isButtonHoldsEnabled = True

def disable_all_button_holds_until_all_released():
    global isButtonHoldsEnabled
    isButtonHoldsEnabled = False

def update_button_logic():
    global isButtonHoldsEnabled, inDemoMode

    if not isGreenPressed and not isYellowPressed and not isRedPressed:
        isButtonHoldsEnabled = True

    if isButtonHoldsEnabled: 
        
        if greenTimeHeld > QUICK_SPRINT_HOLD_TIME and isOneButtonPressed():
                start_sprint(QUICK_SPRINT_LENGTH)

        if inSession:
            
            if yellowTimeHeld > LONG_BREAK_HOLD_TIME and isOneButtonPressed():
                start_break(LONG_BREAK_LENGTH)
            
            
            if greenTimeHeld > END_SESSION_HOLD_TIME and yellowTimeHeld > END_SESSION_HOLD_TIME:
                end_session()
                disable_all_button_holds_until_all_released()
            
        else:

            if yellowTimeHeld > BEDTIME_SHUTDOWN_HOLD_TIME and isOneButtonPressed():
                bedtime()

            if redTimeHeld > ABORT_BEDTIME_PROTOCOL_HOLD_TIME and isOneButtonPressed():
                abort_bedtime_protocol()
            
            if greenTimeHeld > DEMO_MODE_HOLD_TIME and yellowTimeHeld > DEMO_MODE_HOLD_TIME and redTimeHeld > DEMO_MODE_HOLD_TIME:
                leff.start(leff.DEMO_MODE)
                inDemoMode = True
                print("DEMO MODE")

            if inDemoMode and isOneButtonPressed:
                leff.kill_effect()
                inDemoMode = False

