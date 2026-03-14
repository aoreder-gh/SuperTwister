# ==============================================================
# Super Twister 3001
# function for reset button handling
# Used for emergency stop and error handling
# @author    Andreas Reder <aoreder@googlemail.com>
# ==============================================================

import os, sys
import time
import hardware.pi as hpi
import state
from configs.config import RESET_PIN
from utils.debug import dprint

press_time = None
button_was_pressed = False

def setup_reset():
    hpi.pi.set_mode(RESET_PIN, 0)

def poll_reset(root):
    global press_time, button_was_pressed

    reset = hpi.pi.read(RESET_PIN)

    # Taster gedrueckt (angenommen LOW = gedrueckt)
    if reset == 0:
        if not button_was_pressed:
            # first init
            press_time = time.time()
            button_was_pressed = True
            #dprint("Reset pressed")

        # gedrueckt halten pruefen
        elif time.time() - press_time > 3 and button_was_pressed:
            #dprint("Hold 3 sec -> Close window")
            root.destroy()
            os.execv(sys.executable, ['python3'] + sys.argv)
            #sys.exit(0)

    # release button
    else:
        #if button_was_pressed:
            #dprint("Reset release")
        press_time = None
        button_was_pressed = False    

