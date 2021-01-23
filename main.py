from astral import LocationInfo
from astral.sun import sun
import sys
import time
import datetime
import RPi.GPIO as GPIO
import tm1637
import button_listener 
import button_logic
import bedtime_protocol
import session_manager
import light_effects
import output_controller
from global_vars import *

while(True):

    button_listener.listen_to_the_buttons()
    button_logic.update_button_logic()
    session_manager.update_session_manager()
    bedtime_protocol.update_bedtime_protocol()
    light_effects.update_light_effects()
    output_controller.update_output_controller()

    time.sleep(DT)
