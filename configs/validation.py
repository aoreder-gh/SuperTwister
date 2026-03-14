# ==================================================================
# Super Twister 3001
# Parameter CONSTANTS for validation
# Main validation config file with all parameters and allowed values
# @author    Andreas Reder <aoreder@gmail.com>
# ==================================================================

VALIDATION_SERVICE = {
    "DEBUG": {"allowed": ["True", "False"] },
    "FULLSCREEN": {"allowed": ["True", "False"] }, 
    "width": {"allowed": [360, 390, 600, 800, 1020, 1024, 1280, 1400, 1440, 1600, 1920] },
    "height": {"allowed": [360, 390, 600, 800, 1020, 1024, 1280, 1400, 1440, 1600, 1920] },
    "UPDATE_MS": {"min": 1, "max": 1000},
    "DIR_RIGHT": {"allowed": [0, 1]},  
    "DIR_LEFT": {"allowed": [0, 1]},
    "TWIST_MODE": {"allowed": ["normal", "reversed"]},
    "MICROSTEPS": {"allowed": [200, 400, 800, 1600, 3200, 6400]},  
    "PWM_DUTY": {"min": 100000, "max": 999999},   
    "ENCODER_TIME": {"min": 1, "max": 120},   
    "SLEEP_TIME": {"min": 0.001, "max": 0.5},   
    "THROTTLE_START": {"min": 0.01, "max": 0.25},   
    "ACCEL_FAST": {"min": 10, "max": 1000},   
    "ACCEL_SLOW": {"min": 10, "max": 1000},   
    "DECEL_FAST": {"min": 10, "max": 1000},   
    "DECEL_SLOW": {"min": 10, "max": 1000},   
    "RESONANCE_MIN": {"min": 10, "max": 1000},   
    "RESONANCE_MAX": {"min": 10, "max": 1000},   
    }
VALIDATION_OPERATOR = {
    "DEFAULT_PROFILE": {"allowed": ["default", "production", "testing", "debug"]},
    "RAMP_TIME": {"min": 0.1, "max": 10},        
    "STOP_RAMP_TIME": {"min": 0.1, "max": 10}, 
    "STOP_HARD_RPM_THRESHOLD": {"min": 10, "max": 1000}, 
    "PWM_UPDATE_THRESHOLD": {"min": 1, "max": 100}, 
    "MAX_TWIST": {"min": 1, "max": 1000}, 
    "START_RPM": {"min": 1, "max": 1000},  
    "CENTER_RPM": {"min": 10, "max": 150}, 
    "CENTER_OFFSET_STEPS": {"min": -6400, "max": 6400}, 
    "MAX_RPM": {"min": 10, "max": 2500}, 
    "MIN_RPM": {"min": 10, "max": 150}, 
    "STEP_RPM": {"min": 1, "max": 150}, 
    "FAST_STEP": {"min": 10, "max": 600}, 
}