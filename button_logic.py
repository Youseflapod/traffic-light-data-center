import constant_parameters as c # pylint: disable=unused-wildcard-import
import button_listener as bl # pylint: disable=unused-wildcard-import
import session_manager as sm # pylint: disable=unused-wildcard-import
import bedtime_protocol as bp # pylint: disable=unused-wildcard-import
import light_effects as leff

inDemoMode = False

def green_button_clicked():
    print("GREEN BUTTON CLICKED")
    sm.start_sprint(c.STANDARD_SPRINT_LENGTH)
    if sm.inInterruption:
        sm.end_interruption()

def yellow_button_clicked():
    if sm.inSession:
        sm.start_break(c.STANDARD_BREAK_LENGTH)

def red_button_clicked():
    pass

def green_button_just_pressed():
    pass

def yellow_button_just_pressed():
    pass

def red_button_just_pressed():
    pass
    if sm.inSession:
        sm.start_interruption() # because there is no hold function during session, so more immediate

isButtonHoldsEnabled = True

def disable_all_button_holds_until_all_released():
    global isButtonHoldsEnabled
    isButtonHoldsEnabled = False

def update_button_logic():
    global isButtonHoldsEnabled, inDemoMode

    if not bl.isGreenPressed and not bl.isYellowPressed and not bl.isRedPressed:
        isButtonHoldsEnabled = True

    if isButtonHoldsEnabled: 
        
        if bl.greenTimeHeld > c.QUICK_SPRINT_HOLD_TIME and bl.isOneButtonPressed():
                sm.start_sprint(c.QUICK_SPRINT_LENGTH)
                disable_all_button_holds_until_all_released()

        if sm.inSession:
            
            if bl.yellowTimeHeld > c.LONG_BREAK_HOLD_TIME and bl.isOneButtonPressed():
                sm.start_break(c.LONG_BREAK_LENGTH)
                disable_all_button_holds_until_all_released()
            
            
            if bl.greenTimeHeld > c.END_SESSION_HOLD_TIME and bl.yellowTimeHeld > c.END_SESSION_HOLD_TIME:
                sm.end_session()
                disable_all_button_holds_until_all_released()
            
        else:

            if bl.yellowTimeHeld > c.BEDTIME_SHUTDOWN_HOLD_TIME and bl.isOneButtonPressed():
                bp.bedtime()
                disable_all_button_holds_until_all_released()

            if bl.redTimeHeld > c.ABORT_BEDTIME_PROTOCOL_HOLD_TIME and bl.isOneButtonPressed():
                bp.abort_bedtime_protocol()
                disable_all_button_holds_until_all_released()
            
            if bl.greenTimeHeld > c.DEMO_MODE_HOLD_TIME and bl.yellowTimeHeld > c.DEMO_MODE_HOLD_TIME and bl.redTimeHeld > c.DEMO_MODE_HOLD_TIME:
                leff.start(leff.DEMO_MODE)
                inDemoMode = True
                print("DEMO MODE")
                disable_all_button_holds_until_all_released()

            if inDemoMode and bl.isOneButtonPressed():
                leff.kill_effect()
                inDemoMode = False

