import button_listener 
import button_logic
import bedtime_protocol
import session_manager
import light_effects
import output_controller
import debug_light_effects
import constant_parameters as c
import time
import logging
import datetime

logging.basicConfig(filename='app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')

# on boot safety in case I reboot at 11:30 lol
bedtime_protocol.calculate_sunrise_of_tomorrow_and_bedtime()
if datetime.datetime.now() > bedtime_protocol.bedtimeTonight:
    bedtime_protocol.abort_bedtime_protocol()


light_effects.turnOff()


def main():

    while(True):

        button_listener.listen_to_the_buttons()
        button_logic.update_button_logic()
        
        session_manager.update_session_manager()
        bedtime_protocol.update_bedtime_protocol()
        
        light_effects.update_light_effects()
        output_controller.update_output_controller()

        time.sleep(c.DT)

if not debug_light_effects.DEBUG:
    try:
        main()
    except Exception as e:
        logging.error("Main thread exception occurred", exc_info=True)
