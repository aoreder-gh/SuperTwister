# ==============================================================
# Super Twister 3001
# debug
# utility functions for debugging
# @author    Andreas Reder <aoreder@gmail.com>
# ==============================================================

import configs.config as config

def dprint(msg):
    if config.DEBUG:
        print(msg)