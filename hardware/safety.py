# ==============================================================
# Super Twister 3001
# Safety module for emergency stop and safety checks
# @author    Andreas Reder <aoreder@googlemail.com>
# ==============================================================

import hardware.pi as hpi
import state
import time
from configs.config import ESTOP_PIN
from utils.debug import dprint


def setup_safety():
    hpi.pi.set_mode(ESTOP_PIN, 0)
    hpi.pi.write(ESTOP_PIN, 1)

def poll():
    estop = hpi.pi.read(ESTOP_PIN)
    if estop == 0:  # button pressed
        #time.sleep(0.01)  # 10 ms entprellen
        if hpi.pi.read(ESTOP_PIN) == 0:
            state.safety_estop = True
            dprint("Poll read EMERGENCY-Button -Stop- 0")
    else:
        state.safety_estop = False
