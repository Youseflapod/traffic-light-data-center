import button_listener 
import button_logic
import bedtime_protocol
import session_manager
import light_effects
import output_controller
from global_vars import *

bedtime_protocol.calculate_sunrise_of_tomorrow()

while(True):

    button_listener.listen_to_the_buttons()
    button_logic.update_button_logic()
    
    session_manager.update_session_manager()
    bedtime_protocol.update_bedtime_protocol()
    
    light_effects.update_light_effects()
    output_controller.update_output_controller()

    time.sleep(DT)
