# ==============================================================
# Super Twister 3001
# Main function for motor control
# Includes start, stop and centering functions
# @author    Andreas Reder <aoreder@gmail.com>
# ==============================================================

from configs.config import *
from logic.config_io import save_config
from logic.controller import *
from logic.state_machine import set_state
from utils.debug import dprint


def start_motor():
    if state.safety_estop:
        set_state(SAFE)
        return
    state.started_by_button = True
    state.running = True
    set_state(RUNNING)
    start_motor_hw(state.direction, state.twist_mode)


def stop_motor():
    state.started_by_button = False
    state.running = False
    set_state(IDLE)
    save_config()

def toggle_motor(event=None):
    toggle_motor_hw()

def start_centering():
    state.center_steps_done = 0.0
    state.running = True
    state.center_phase = FIND_REED
    set_state(CENTERING)
    start_motor_hw(state.direction, state.twist_mode)
