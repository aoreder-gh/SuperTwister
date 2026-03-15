# ==============================================================
# Super Twister 3001
# Config Load/Save Functions
# @author    Andreas Reder <aoreder@gmail.com>
# ==============================================================

import json
import os
import state

from configs.config import CONFIG_DIR, RECIPE_DIR, DEFAULT_PROFILE, TWIST_RPM
from utils.debug import dprint
from utils.logger import setup_logger


def _p(p): return f"{CONFIG_DIR}/{p}.json"


def _r(p): return f"{RECIPE_DIR}/{p}.json"


def save_config(profile=None):
    if profile is None: profile = DEFAULT_PROFILE
    os.makedirs(CONFIG_DIR, exist_ok=True)
    with open(_p(profile), "w") as f:
        json.dump({            
            "target_rpm": state.target_rpm,
            "direction": state.direction,
            "remaining_turns": state.remaining_turns,
            "loaded_turns": state.loaded_turns,
            "completed_turns": state.completed_turns,
            "language": getattr(state, "language", "de"),
            "twist_mode": state.twist_mode,
            "throttle_min_v": state.throttle_min_v,
            "throttle_max_v": state.throttle_max_v,
            "current_profile": state.current_profile
        }, f, indent=4)
    dprint(f"Config saved to {f}")


def load_config(profile=None):
    if profile is None: profile = DEFAULT_PROFILE
    with open(_p(profile)) as f:
        d = json.load(f)
    state.target_rpm = d.get("target_rpm", state.target_rpm)
    state.remaining_turns = d.get("remaining_turns", state.remaining_turns)
    state.loaded_turns = d.get("loaded_turns", state.loaded_turns)
    if state.loaded_turns > 0:
        state.endless_turns = 1
    state.direction = d.get("direction", state.direction)
    state.language = d.get("language", state.language)
    state.twist_mode = d.get("twist_mode", state.twist_mode)
    state.throttle_min_v = d.get("throttle_min_v", 0.9)
    state.throttle_max_v = d.get("throttle_max_v", 4.1)
    profile = d.get("current_profile", state.current_profile)
    dprint(f"Config loaded from {f}")
    dprint(profile)

    load_receipe(profile)
    setup_logger(profile)


def load_receipe(profile=None):
    if profile is None: profile = state.current_profile
    with open(_r(profile)) as f:
        d = json.load(f)
    

    state.target_rpm = d["rpm"]
    state.remaining_turns = d["turns"]
    state.loaded_turns = d["turns"]
    if state.loaded_turns > 0:
        state.endless_turns = 0
    state.loaded_rpm = d["rpm"]
    state.loaded_turns = d["turns"]
    state.current_profile = d["name"]

    # If twist mode is active when loading a recipe, ensure we start at the
    # twist maximum speed.
    if getattr(state, "twist_mode", False):
        state.target_rpm = TWIST_RPM
        #state.loaded_rpm = TWIST_RPM

    dprint(f"Recipe loaded from {f}")
