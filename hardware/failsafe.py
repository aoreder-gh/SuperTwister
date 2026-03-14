# ==============================================================
# Super Twister 3001
# function for failsafe motor stop
# Used for emergency stop and error handling
# @author    Andreas Reder <aoreder@gmail.com>
# ==============================================================

import hardware.pi as hpi
from configs.config import STEP_PIN, ENA_AB, ENA_RELEASED
from utils.debug import dprint


def gpio_failsafe():

    try:
        if not hpi.pi:
            dprint("FAILSAFE: pigpio not available")
            return

        # STOP STEP SIGNAL
        hpi.pi.hardware_PWM(STEP_PIN, 0, 0)

        # DISABLE DRIVER (HIGH = disable)
        hpi.pi.write(ENA_AB, ENA_RELEASED)

        dprint("FAILSAFE: Motor disabled safely")

    except Exception as e:
        dprint(f"FAILSAFE ERROR: {e}")