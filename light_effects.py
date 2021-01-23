from global_vars import *
from output_controller import *

def end_session():
    set_light_and_brightness((0,0,0,0))

def start_sprint():
    set_light_and_brightness(SPRINT_L_B)

def start_break():
    set_light_and_brightness(BREAK_L_B)

def start_interruption():
    set_light_and_brightness(INTERRUPTION_L_B)

def past_break():
    pass

def entering_overtime():
    pass

def past_bedtime():
    pass

def morning():
    pass


def update_light_effects():
    pass