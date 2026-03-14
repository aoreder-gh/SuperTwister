# ==============================================================
# Super Twister 3001
# state
# global state variables
# @author    Andreas Reder <aoreder@gmail.com>
# ==============================================================

# if throttle or button is used
started_by_button = False
# Global shared state
machine_state = "IDLE"   # IDLE, RUNNING, CENTERING, SAFE, ERROR
# center state
center = 0.0
center_phase = None          # "FIND_REED" | "MOVE_BACK"
center_steps_done = 0.0
center_guard_active = False
center_start_time = 0.0
center_total_steps = 0.0
center_initial_reed = 0.0
center_steps_to_reed = 0.0
# default language
language = "DE"
# motor
running = False
direction = True
twist_mode = False
# values for frontend
loaded_rpm = 600
target_rpm = 600
actual_rpm = 0.0
loaded_turns = 0
limit_reached = False
remaining_turns = 0
completed_turns = 0
# some standards for motor
endless_turns = 0
motor_locked = False
error = None
current_profile = "default"
last_hz = 0
# ramp vars
ramp_active = False
ramp_start_time = 0.0
ramp_start_rpm = 0.0
ramp_target_rpm = 0.0
# Safety
safety_estop = False
cpu_temp = 0.0
# Roles
user_role = "OPERATOR"  # OPERATOR / SERVICE / CALIBRATION / STATISTIC
# Throttle
throttle_blocked = False
throttle_percent = 0.0
last_throttle_time = 0.0
# Throttle calibration (Volt)
throttle_min_v = 0.6
throttle_max_v = 4.1
# wizard steps
wizard_active = False
wizard_bow_type = None
wizard_step_index = 0
wizard_completed_steps = {}
