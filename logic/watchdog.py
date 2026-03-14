# ==============================================================
# Super Twister 3001
# watchdog for RPI 4
# helper function for RPI4 to check if pigpiod is running
# @author    Andreas Reder <aoreder@gmail.com>
# ==============================================================

import threading
from hardware.failsafe import gpio_failsafe
import hardware.pi as hpi
import state
from utils.debug import dprint


def start_watchdog(shutdown_event, interval=2):

    def loop():

        pigpio_lost = False

        while not shutdown_event.wait(interval):

            try:
                # -------- HARD CONNECTION CHECK --------
                if not hpi.pi:
                    raise RuntimeError("pigpio instance missing")

                # This forces real communication
                hpi.pi.get_current_tick()

                # If we reach here → connection OK
                pigpio_lost = False

            except Exception as e:

                if not pigpio_lost:
                    # Only trigger once
                    pigpio_lost = True

                    state.error = "PIGPIO_LOST"
                    state.running = False
                    state.machine_state = "ERROR"

                    gpio_failsafe()

                    dprint("WATCHDOG: pigpio lost → failsafe activated")

            # Optional: future reconnect logic could go here

        dprint("WATCHDOG: shutdown clean")

    threading.Thread(
        target=loop,
        daemon=False
    ).start()
