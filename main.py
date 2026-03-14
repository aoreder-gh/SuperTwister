#  /**
#   * Super Twister 3001
#   *
#   * @author    Andreas Reder
#   * @version   1.1.0
#   */

import atexit
import os
import sys
import signal
import threading

import hardware.pi as hpi
from hardware.failsafe import gpio_failsafe
from hardware.reed_input import setup_reed
from hardware.safety import setup_safety
from hardware.reset import setup_reset
from logic.config_io import load_config, save_config
from logic.controller import setup_motor, run_motor_loop
from logic.watchdog import start_watchdog
from ui.main_window import create_main_window
from utils.debug import dprint

# error logging redirect to a file. For later use...
#logs_folder = os.path.join(os.path.dirname(__file__), "logs")
#os.makedirs(logs_folder, exist_ok=True)
#log_file=os.path.join(logs_folder, "error.log")

# lock file for prevent double start
LOCKFILE = "/tmp/supertwister.lock"
shutdown_event = threading.Event()
_motor_thread = None
_is_shutting_down = False
pi = None

#sys.stderr=open(log_file, "a")

# ============================================================
# LOCK HANDLING
# ============================================================

def create_lock():
    if os.path.exists(LOCKFILE):
        with open(LOCKFILE, "r", encoding="utf-8") as f:
            old_pid = int(f.read().strip())
        try:
            os.kill(old_pid, 0)
            print("SuperTwister already running.")
            sys.exit(1)
        except ProcessLookupError:
            os.remove(LOCKFILE)

    with open(LOCKFILE, "w", encoding="utf-8") as f:
        f.write(str(os.getpid()))


def cleanup_lock():
    if os.path.exists(LOCKFILE):
        os.remove(LOCKFILE)


# ============================================================
# SHUTDOWN HANDLING
# ============================================================

def shutdown():
    global _is_shutting_down

    if _is_shutting_down:
        return

    _is_shutting_down = True

    save_config()
    gpio_failsafe()
    cleanup_lock()
    
    print("Shutting down SuperTwister...")

    shutdown_event.set()

    if _motor_thread and _motor_thread.is_alive():
        _motor_thread.join(timeout=2)


def signal_handler(signum, frame):
    shutdown()
    sys.exit(0)


# ============================================================
# MAIN
# ============================================================

def main():
    global pi, _motor_thread

    create_lock()

    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    atexit.register(shutdown)

    pi = hpi.connect_pi()

    if not pi or not pi.connected:
        print("ERROR: Cannot connect to pigpio daemon.")
        cleanup_lock()
        sys.exit(1)

    load_config()
    setup_motor()
    setup_safety()
    setup_reed()
    setup_reset()

    start_watchdog(shutdown_event)

    _motor_thread = threading.Thread(
        target=run_motor_loop,
        args=(shutdown_event,),
        daemon=True
    )
    _motor_thread.start()

    create_main_window()

    shutdown()

if __name__ == "__main__":
    main()