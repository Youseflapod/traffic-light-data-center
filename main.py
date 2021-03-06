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

light_effects.turnOff()

# on boot safety in case I reboot at 11:30 lol
bedtime_protocol.calculate_sunrise_of_tomorrow_and_bedtime()
bedtime_protocol.update_bedtime_protocol()

if c.TZ.localize(datetime.datetime.now()) > bedtime_protocol.bedtimeTonight:
    bedtime_protocol.abort_bedtime_protocol()
else:
    light_effects.start(light_effects.END_SESSION) # boot colors



def main():
    print("started successfully!")

    while(True):
        startTime = time.time()

        button_listener.listen_to_the_buttons()
        button_logic.update_button_logic()

        session_manager.update_session_manager()
        bedtime_protocol.update_bedtime_protocol()

        light_effects.update_light_effects()
        output_controller.update_output_controller()

        sleeptime = c.DT - (time.time() - startTime)
        if sleeptime > 0:
            time.sleep(sleeptime)

if not debug_light_effects.DEBUG:
    try:
        main()
    except Exception as e:
        logging.error("Main thread exception occurred", exc_info=True)
        raise Exception(e)