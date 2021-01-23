from global_vars import *

def set_light(rgb_tuple):
    r, g, b = rgb_tuple

def set_brightness(a): 
    pass

def set_light_and_brightness(rgba_tuple):
    r,g,b,a = rgba_tuple
    set_light((r,g,b))
    set_brightness(a)

def display_clock_time(dateInSeconds):
    pass

def display_min_and_sec(seconds):
    pass

def update_output_controller():
    pass