# ==============================================================
# Super Twister 3001
# Parameter CONSTANTS
# Main config file with all parameters and default values
# @author    Andreas Reder <aoreder@gmail.com>
# ==============================================================

# fixed const
APP_NAME = "Super Twister 3001"
# status names
SAFE = "SAFE"
RUNNING = "RUN"
IDLE = "IDLE"
SERVICE = "SERVICE"
OPERATOR = "OPERATOR"
CALIBRATION = "CALIBRATION"
STATISTIC = "STATISTIC"
CENTERING = "CENTERING"
FIND_REED = "FIND_REED"
DISABLED = "disabled"
NORMAL = "normal"
DE = "DE"
EN = "EN"
ALERT_CPU_TEMP = 65.0
TWIST_RPM = 150
# adjustments
SVC_FONT = ("Arial", 14)
SVC_FONT_BOLD = ("Arial", 14, "bold")
LBL_FONT = ("Arial", 16)
PROGRESS_FONT = ("Arial", 18, "bold")
TARGET_FONT = ("Arial", 20)
BUTTON_FONT = ("Arial", 24)
BUTTON_FONT_BOLD = ("Arial", 24, "bold")
BIG_FONT = ("Arial", 28, "bold")
BIG_BIG_FONT = ("Arial", 40, "bold")
BIG_FONT_MINUS = ("Arial", 52, "bold")
IMG_PATH = "img/"
PAD_X = 10
PAD_Y = 10
# folder config
CONFIG_DIR = "configs"
RECIPE_DIR = "recipes"
# set defaults
ENA_LOCKED = 0
ENA_RELEASED = 1
CENTERING = "CENTERING"
FIND_REED = "FIND_REED"
MOVE_BACK = "MOVE_BACK"
# configure the pin
STEP_PIN = 12
DIR_A = 16
DIR_B = 26
ENA_AB = 19
REED_PIN = 20
ESTOP_PIN = 27
RESET_PIN = 7

# changeable vars

# changeable by SERVICE
# debug mode allows printing messages on the command line
DEBUG = False
# full screen mode
FULLSCREEN = True
# declare size of app if FULLSCREEN = FALSE
width = 1024
height = 600
UPDATE_MS = 100
# set for centering
DIR_RIGHT = 0
DIR_LEFT = 1
# set some defaults for twisting #normal, #reversed
TWIST_MODE = 'reversed'
# configure stepper
MICROSTEPS = 800
PWM_DUTY = 650000
ENCODER_TIME = 60.0
SLEEP_TIME = 0.005
# throttle adjustments
THROTTLE_START = 0.05
# Additions for HW PLUS
ACCEL_FAST = 80
ACCEL_SLOW = 40
DECEL_FAST = 120
DECEL_SLOW = 60
RESONANCE_MIN = 120
RESONANCE_MAX = 400
# changeable by OPERATOR
# profile name
DEFAULT_PROFILE = 'default'
# Additions for HW PLUS
RAMP_TIME = 3
STOP_RAMP_TIME = 0.4
STOP_HARD_RPM_THRESHOLD = 300
PWM_UPDATE_THRESHOLD = 10
# set some defaults for twisting
MAX_TWIST = 400
START_RPM = 150
# centering const
CENTER_RPM = 100
CENTER_OFFSET_STEPS = 220
# throttle
MAX_RPM = 2500
MIN_RPM = 20
STEP_RPM = 10
FAST_STEP = 100
