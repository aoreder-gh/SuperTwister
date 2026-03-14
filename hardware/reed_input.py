# ==============================================================
# Super Twister 3001
# Hardware abstraction layer for Reed Switch input
# Reads the state of the reed switch for centering
# @author    Andreas Reder <aoreder@googlemail.com>
# ==============================================================

import hardware.pi as hpi
import state
from configs.config import REED_PIN
from utils.debug import dprint

INPUT = 0
PUD_UP = 2

def setup_reed():
    hpi.pi.set_mode(REED_PIN, INPUT)
    hpi.pi.set_pull_up_down(REED_PIN, PUD_UP)


def read_reed():
    value = (hpi.pi.read(REED_PIN) == 0)  # True = Reed aktiv
    state.center = value
    dprint("REED:" + str(value))
