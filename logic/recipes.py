#  /**
#   * Super Twister 3001
#   *
#   * @author    Andreas Reder <aoreder@gmail.com>
#   *
#   * @copyright Andreas Reder
#   * @version   1.0.0
#   */

import json
import os
import state

from configs.config import RECIPE_DIR
from logic.config_io import save_config
from utils.debug import dprint


def list_recipes():
    return [f for f in os.listdir(RECIPE_DIR) if f.endswith(".json")]


def load_recipe(name):
    with open(os.path.join(RECIPE_DIR, name)) as f:
        r = json.load(f)
    return r


def _p(p): return f"{RECIPE_DIR}/{p}.json"


def save_recipe(profile=None):
    if profile is None: profile = state.current_profile
    os.makedirs(RECIPE_DIR, exist_ok=True)
    with open(_p(profile), "w") as f:
        json.dump({
            "name": profile,
            "rpm": state.target_rpm,
            "turns": state.remaining_turns,
            "direction": "cw" if state.direction == True else "ccw",
            "twist_mode": state.twist_mode
        }, f, indent=4)
    state.current_profile = profile
    save_config()
    dprint(f"Config saved to {f}")
