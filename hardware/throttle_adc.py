# ==============================================================
# Super Twister 3001
# Throttle ADC Reading
# Reads throttle voltage from ADS1115 and updates state
# @author    Andreas Reder <aoreder@gmail.com>
# ==============================================================


import time
import state
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
from utils.debug import dprint

# I2C initialize
i2c = busio.I2C(board.SCL, board.SDA)

# ADS1115 initialize
try:
    ads = ADS.ADS1115(i2c)
    dprint("ADS1115 gefunden ✅")

except ValueError as e:
    dprint("Fehler beim Initialisieren des ADS1115 ❌")
    dprint(e)
    ads = None  # Wichtig, damit dein Programm weiterlaufen kann

# Correct channel access to connector 1 (of 4)
chan = None
if ads is not None:
    chan = AnalogIn(ads, 0)
    
def update_throttle():
    if chan is None:
        # no ADC → no Update
        dprint("ADC not available – throttle skipped")
        return
    v = chan.voltage

    # Clamp with calibrated values
    v = max(state.throttle_min_v, min(state.throttle_max_v, v))
    percent = (v - state.throttle_min_v) / (
        state.throttle_max_v - state.throttle_min_v
    )

    state.throttle_percent = max(0.0, min(1.0, percent))
    state.last_throttle_time = time.time()
    dprint("Throttle " + str(percent) + '%')
