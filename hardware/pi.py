# ==============================================================
# Super Twister 3001
# Hardware abstraction layer for Raspberry Pi 4 and 5
# Uses pigpio for Pi4 and libgpiod for Pi5
# @author    Andreas Reder <aoreder@gmail.com>
# ==============================================================

import os
import threading
import time

pi = None


# ------------------------------------------------
# Detect hardware
# ------------------------------------------------

def detect_pi5():

    try:
        with open("/proc/device-tree/model") as f:
            return "Raspberry Pi 5" in f.read()
    except:
        return False


# ------------------------------------------------
# STEP ENGINE (Pi5)
# ------------------------------------------------

class StepEngine:

    def __init__(self, write_func):

        self.write = write_func
        self.pin = None
        self.freq = 0
        self.running = False
        self.thread = None

    def start(self, pin, freq):

        self.pin = pin
        self.freq = freq

        if self.thread is None:

            self.running = True
            self.thread = threading.Thread(
                target=self.loop,
                daemon=True
            )
            self.thread.start()

    def stop(self):

        self.running = False
        self.thread = None

    def set_freq(self, freq):

        self.freq = freq

    def loop(self):

        next_time = time.perf_counter()

        while self.running:

            freq = self.freq

            if freq <= 0:
                time.sleep(0.01)
                continue

            period = 1.0 / freq
            half = period / 2

            next_time += half
            self.write(self.pin, 1)

            while time.perf_counter() < next_time:
                pass

            next_time += half
            self.write(self.pin, 0)

            while time.perf_counter() < next_time:
                pass


# ------------------------------------------------
# MAIN WRAPPER
# ------------------------------------------------

class Pi:

    def __init__(self):

        self.is_pi5 = detect_pi5()
        self.connected = False
        self.lines = {}
        self.line_modes = {}

        if self.is_pi5:
            self._init_pi5()
        else:
            self._init_pi4()

    # ------------------------------------------------
    # Pi4
    # ------------------------------------------------

    def _init_pi4(self):

        import pigpio

        self.pi = pigpio.pi()

        if self.pi and self.pi.connected:
            self.connected = True

    # ------------------------------------------------
    # Pi5
    # ------------------------------------------------

    def _init_pi5(self):

        import gpiod

        try:

            chip_name = "gpiochip4" if os.path.exists("/dev/gpiochip4") else "gpiochip0"

            self.chip = gpiod.Chip(chip_name)

            self.step_engine = StepEngine(self.write)

            self.connected = True

        except Exception:

            self.connected = False

    # ------------------------------------------------
    # INTERNAL PIN REQUEST
    # ------------------------------------------------

    def _ensure_line(self, pin, mode):

        if not self.is_pi5:
            return

        if pin in self.lines:
            return self.lines[pin]

        import gpiod

        line = self.chip.get_line(pin)

        if mode == "out":

            line.request(
                consumer="supertwister",
                type=gpiod.LINE_REQ_DIR_OUT
            )

        else:

            line.request(
                consumer="supertwister",
                type=gpiod.LINE_REQ_DIR_IN
            )

        self.lines[pin] = line

        return line

    # ------------------------------------------------
    # SET MODE
    # ------------------------------------------------

    def set_mode(self, pin, mode):

        if not self.is_pi5:

            if mode in (1, "output"):
                self.pi.set_mode(pin, 1)
            else:
                self.pi.set_mode(pin, 0)

            return

        import gpiod

        if mode in (1, "output"):

            line = self.chip.get_line(pin)
            line.request(
                consumer="supertwister",
                type=gpiod.LINE_REQ_DIR_OUT
            )

            self.lines[pin] = line
            self.line_modes[pin] = "out"

        else:

            line = self.chip.get_line(pin)
            line.request(
                consumer="supertwister",
                type=gpiod.LINE_REQ_DIR_IN,
                flags=gpiod.LINE_REQ_FLAG_BIAS_PULL_UP
            )

            self.lines[pin] = line
            self.line_modes[pin] = "in"


    # ------------------------------------------------
    # WRITE
    # ------------------------------------------------

    def write(self, pin, value):
        if not self.is_pi5:
            self.pi.write(pin, value)
            return

        if self.line_modes.get(pin) != "out":

            # neu initialisieren als output
            import gpiod

            line = self.chip.get_line(pin)

            line.request(
                consumer="supertwister",
                type=gpiod.LINE_REQ_DIR_OUT
            )

            self.lines[pin] = line
            self.line_modes[pin] = "out"

        line = self.lines[pin]

        line.set_value(value)


    # ------------------------------------------------
    # READ
    # ------------------------------------------------

    def read(self, pin):

        if not self.is_pi5:

            return self.pi.read(pin)

        line = self._ensure_line(pin, "in")

        return line.get_value()


    # ------------------------------------------------
    # INTERRUPT (Reed Sensor etc.)
    # ------------------------------------------------

    def callback(self, pin, func):

        line = self._ensure_line(pin, "in")

        def watcher():

            while True:

                if line.event_wait(sec=1):

                    line.event_read()

                    func()

        threading.Thread(target=watcher, daemon=True).start()


    # ------------------------------------------------
    # HARDWARE PWM
    # ------------------------------------------------

    def hardware_PWM(self, pin, freq, duty):

        if not self.is_pi5:

            self.pi.hardware_PWM(pin, freq, duty)
            return

        if freq == 0:

            self.step_engine.stop()
            return

        self.step_engine.start(pin, freq)
        self.step_engine.set_freq(freq)


    # ------------------------------------------------
    # CLEANUP
    # ------------------------------------------------

    def stop(self):

        if not self.is_pi5:

            self.pi.stop()

        else:

            if self.step_engine:
                self.step_engine.stop()

    # ------------------------------------------------
    # reed_input.py needs pull-up/pull-down, but Pi5 does not support changing it after line request
    # ------------------------------------------------

    def set_pull_up_down(self, pin, pud):

        if not self.is_pi5:
            self.pi.set_pull_up_down(pin, pud)

        # Pi5: do nothing, we set pull-up during line request

    # ------------------------------------------------
    # watchdog etc. may need current tick
    # ------------------------------------------------

    def get_current_tick(self):

        if not self.is_pi5:
            return self.pi.get_current_tick()

        import time
        return int(time.monotonic() * 1_000_000)
        

# ------------------------------------------------
# PUBLIC CONNECT
# ------------------------------------------------

def connect_pi():

    global pi

    if pi is None:

        pi = Pi()

    return pi
