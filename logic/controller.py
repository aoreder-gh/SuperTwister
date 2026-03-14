# ==============================================================
# Super Twister 3001
# controller.py --- Main control loop and motor management
# @author    Andreas Reder <aoreder@gmail.com>
# ==============================================================

import time

import hardware.pi as hpi
import state
from configs.config import *
from hardware.reed_input import read_reed
from hardware.safety import poll
from hardware.throttle_adc import update_throttle
from utils.debug import dprint

# ----------------------------------------
# AUTO CENTERING CONTROL
# ----------------------------------------

CENTER_FAST = 0
CENTER_LEAVE = 1
CENTER_SCAN_ON = 2
CENTER_SCAN_OFF = 3
CENTER_MOVE_CENTER = 4


# ----------------------------------------
# MOTOR SETUP
# ----------------------------------------

def setup_motor():
    hpi.pi.set_mode(STEP_PIN, 1)
    hpi.pi.set_mode(DIR_A, 1)
    hpi.pi.set_mode(DIR_B, 1)
    hpi.pi.set_mode(ENA_AB, 1)
    stop_motor_hw()

# ----------------------------------------
# START MOTOR HARDWARE
# ----------------------------------------

def start_motor_hw(direction, twist):

    # base direction Motor A
    dir_a = direction

    # Twist define direction Motor B
    if twist:
        dir_b = not direction
    else:
        dir_b = direction

    # Twist Mode global inversion
    if TWIST_MODE == "reversed":
        dir_b = not dir_b

    # globale right direction inversion for centering
    if DIR_RIGHT == 0:
        dir_a = not dir_a
        dir_b = not dir_b

    hpi.pi.write(DIR_A, dir_a)
    hpi.pi.write(DIR_B, dir_b)

    hpi.pi.write(ENA_AB, ENA_LOCKED)

    state.motor_locked = True
    state.direction = direction

# ----------------------------------------
# TOGGLE MOTOR HARDWARE (block or unblock)
# ----------------------------------------

def toggle_motor_hw():
    state.motor_locked = True if not state.motor_locked else False
    hpi.pi.write(ENA_AB, ENA_LOCKED if state.motor_locked else ENA_RELEASED)

# ----------------------------------------
# STOP MOTOR HARDWARE
# ----------------------------------------

def stop_motor_hw():
    hpi.pi.write(ENA_AB, ENA_RELEASED)
    hpi.pi.hardware_PWM(STEP_PIN, 0, 0)
    state.actual_rpm = 0
    state.motor_locked = False

# ----------------------------------------
# RPM ACCELERATION - DECCELERATION CONTROL
# ----------------------------------------

def smoothstep(start, target, elapsed, duration):

    if duration <= 0:
        return target

    x = min(max(elapsed / duration, 0.0), 1.0)

    s = 3*x*x - 2*x*x*x

    return start + (target - start) * s

# ----------------------------------------
# RPM CONTROL
# ----------------------------------------

def set_rpm(rpm: float):

    # -------- SANITY CHECK --------
    if rpm is None:
        return

    if rpm < 0:
        rpm = 0

    # -------- STOP CONDITION --------
    if rpm <= 0.0:
        if state.last_hz != 0:
            stop_motor_hw()
            state.last_hz = 0
        state.actual_rpm = 0.0
        return

    # -------- CALCULATE FREQUENCY --------
    hz = (rpm * MICROSTEPS) / ENCODER_TIME

    # round to nearest int (hardware requires int)
    hz = int(round(hz))

    # small frequency dither to avoid resonance lock
    if hz > 2000:
        hz += (state.last_hz % 3) - 1

    if hz < 1:
        hz = 1

    # -------- UPDATE PWM ONLY IF CHANGED --------
    if abs(hz - state.last_hz) >= PWM_UPDATE_THRESHOLD:
        try:
            hpi.pi.hardware_PWM(STEP_PIN, hz, PWM_DUTY)
            state.last_hz = hz
            #print("RPM:", rpm, "Hz:", hz)
        except Exception as e:
            print("PWM error:" + str(e))
            return

    state.actual_rpm = rpm

# ----------------------------------------
# MAIN MOTOR LOOP
# ----------------------------------------

def run_motor_loop(shutdown_event=None):

    last = time.time()

    while not (shutdown_event and shutdown_event.wait(SLEEP_TIME)):

        now = time.time()
        dt = now - last
        last = now

        # -------------------------------------------------
        # 0 SAFETY
        # -------------------------------------------------        
        poll()
        
        if state.safety_estop:
            set_rpm(0)
            stop_motor_hw()
            state.running = False
            state.machine_state = SAFE
            continue

        # -------------------------------------------------
        # 1 SERVICE MODE
        # -------------------------------------------------
        if state.machine_state == SERVICE:
            state.ramp_active = False
            set_rpm(0)
            continue

        # -------------------------------------------------
        # 2 THROTTLE UPDATE
        # -------------------------------------------------
        if state.machine_state != SERVICE:
            update_throttle()
        
        throttle_active = state.throttle_percent > THROTTLE_START

        if not throttle_active:
            state.limit_reached = False

        if throttle_active and not state.running and not state.limit_reached and not state.machine_state == SERVICE:
            state.running = True
            state.machine_state = RUNNING
            state.started_by_button = False
            start_motor_hw(state.direction, state.twist_mode)

        if (
            state.running
            and state.machine_state == RUNNING
            and not throttle_active
            and not state.started_by_button
        ):
            state.running = False
            state.machine_state = IDLE

        # -------------------------------------------------
        # 3 CENTERING MODE (precision reed centering)
        # -------------------------------------------------
        if state.machine_state == CENTERING:

            # ---------------- INIT ----------------
            if not getattr(state, "center_guard_active", False):

                state.center_guard_active = True
                state.center_phase = CENTER_FAST

                state.center_steps = 0.0
                state.center_edge_on = None
                state.center_edge_off = None

                state.last_reed = state.center
                state.center_start_time = time.monotonic()

                dprint("CENTERING start")

            # ---------- step calculation ----------
            steps_per_sec = (state.actual_rpm / ENCODER_TIME) * MICROSTEPS
            delta_steps = abs(steps_per_sec * dt)
            state.center_steps += delta_steps

            read_reed()
            reed = state.center

            # -------- TIMEOUT CHECK --------
            if time.monotonic() - state.center_start_time > 2.0:

                dprint("CENTERING timeout → skip")

                set_rpm(0)

                state.machine_state = IDLE
                state.running = False
                state.center_guard_active = False
                state.center_phase = None

                continue

            # --------- EDGE DETECTION -------------
            rising_edge = reed and not state.last_reed
            falling_edge = not reed and state.last_reed
            state.last_reed = reed

            # -------------------------------------
            # PHASE 1 FAST APPROACH
            # -------------------------------------
            if state.center_phase == CENTER_FAST:

                start_motor_hw(DIR_RIGHT, state.twist_mode)
                set_rpm(CENTER_RPM)

                if reed:
                    set_rpm(0)
                    state.center_phase = CENTER_LEAVE
                    dprint("Reed detected (fast)")

            # -------------------------------------
            # PHASE 2 LEAVE REED
            # -------------------------------------
            elif state.center_phase == CENTER_LEAVE:

                start_motor_hw(DIR_RIGHT, state.twist_mode)
                set_rpm(CENTER_RPM)

                if not reed:
                    set_rpm(0)
                    state.center_steps = 0
                    state.center_phase = CENTER_SCAN_ON
                    dprint("Reed cleared")

            # -------------------------------------
            # PHASE 3 SLOW SCAN → ON EDGE
            # -------------------------------------
            elif state.center_phase == CENTER_SCAN_ON:

                start_motor_hw(DIR_LEFT, state.twist_mode)
                set_rpm(CENTER_RPM * 0.3)

                if rising_edge:
                    state.center_edge_on = state.center_steps
                    dprint(f"Reed ON edge at {state.center_edge_on:.1f}")
                    state.center_phase = CENTER_SCAN_OFF

            # -------------------------------------
            # PHASE 4 SLOW SCAN → OFF EDGE
            # -------------------------------------
            elif state.center_phase == CENTER_SCAN_OFF:

                start_motor_hw(DIR_LEFT, state.twist_mode)
                set_rpm(CENTER_RPM * 0.3)

                if falling_edge:
                    state.center_edge_off = state.center_steps
                    set_rpm(0)

                    dprint(f"Reed OFF edge at {state.center_edge_off:.1f}")

                    state.center_target = (
                        (state.center_edge_on + state.center_edge_off) / 2
                    ) + CENTER_OFFSET_STEPS

                    dprint(f"Center target step {state.center_target:.1f}")

                    state.center_phase = CENTER_MOVE_CENTER
                    state.center_steps = 0

            # -------------------------------------
            # PHASE 5 MOVE TO CENTER
            # -------------------------------------
            elif state.center_phase == CENTER_MOVE_CENTER:

                start_motor_hw(DIR_RIGHT, state.twist_mode)
                set_rpm(CENTER_RPM * 0.5)

                if state.center_steps >= state.center_target:

                    set_rpm(0)

                    dprint("CENTERING finished")

                    state.machine_state = IDLE
                    state.running = False
                    state.center_guard_active = False
                    state.center_phase = None

            continue

        # -------------------------------------------------
        # 4 RPM CONTROL STRUCTURED
        # -------------------------------------------------

        if not state.running:
            desired_rpm = 0
        else:
            if throttle_active:
                scale = (state.throttle_percent - THROTTLE_START) / (1.0 - THROTTLE_START)
                scale = max(0.0, min(1.0, scale))
                desired_rpm = MIN_RPM + scale * (state.target_rpm - MIN_RPM)
            else:
                desired_rpm = state.target_rpm

        # -------------------------------------------------
        # 5 RESONANCE ZONE SKIP
        # -------------------------------------------------

        if not throttle_active and state.machine_state == RUNNING:

            if RESONANCE_MIN < desired_rpm < RESONANCE_MAX and desired_rpm > state.actual_rpm:
                desired_rpm = RESONANCE_MAX
               
        # -------------------------------------------------
        # 6 AUTO DECELERATION NEAR TARGET (dynamic slowdown)
        # -------------------------------------------------
        # If remaining_turns are active, gradually reduce RPM
        # when approaching the final turns. The slowdown distance
        # scales dynamically with current speed to ensure
        # smooth and predictable stopping behavior.

        if state.remaining_turns > 0 and state.machine_state == RUNNING and not throttle_active:

            current_rpm = state.actual_rpm
            target_rpm = max(1.0, state.target_rpm)

            BASE_SLOWDOWN_TURNS = 6.0      # minimum braking distance
            MAX_EXTRA_TURNS = 12.0         # additional braking distance at high RPM
            MIN_END_RPM = min(40, desired_rpm)  # prevent artificial acceleration

            # Ratio between current speed and target speed
            speed_ratio = current_rpm / target_rpm
            speed_ratio = max(0.0, min(1.0, speed_ratio))

            # Dynamic braking distance
            slowdown_turns = BASE_SLOWDOWN_TURNS + (MAX_EXTRA_TURNS * speed_ratio)

            # Enter braking zone
            if state.remaining_turns < slowdown_turns:

                # Normalize remaining distance
                factor = state.remaining_turns / slowdown_turns
                factor = max(0.0, min(1.0, factor))

                # Nonlinear braking curve for smoother deceleration
                factor = factor ** 3

                new_target = MIN_END_RPM + factor * (target_rpm - MIN_END_RPM)

                # Restart ramp if necessary to enforce braking
                if not state.ramp_active or abs(new_target - state.ramp_target_rpm) > 10:
                    state.ramp_active = True
                    state.ramp_start_time = time.monotonic()
                    state.ramp_start_rpm = current_rpm
                    state.ramp_target_rpm = new_target

                desired_rpm = new_target
        
        current = state.actual_rpm

        # -------------------------------------------------
        # 7 TURN COUNTER UPDATE
        # Tracks completed turns and handles automatic stop
        # -------------------------------------------------

        if state.machine_state == RUNNING and state.actual_rpm > 0:

            delta_turns = (state.actual_rpm / ENCODER_TIME) * dt

            # In twist mode both sides rotate against each other, so the
            # twist count should reflect the combined movement.
            if state.twist_mode:
                delta_turns *= 2

            state.completed_turns += delta_turns

            if state.remaining_turns > 0:
                state.remaining_turns = max(0.0, state.remaining_turns - delta_turns)

                if state.remaining_turns <= 0:
                    state.running = False
                    state.machine_state = IDLE
                    state.limit_reached = True

        # -------------------------------------------------
        # 8 THROTTLE MODE → DIRECT CONTROL
        # -------------------------------------------------
        if throttle_active and state.machine_state == RUNNING:

            state.ramp_active = False
            set_rpm(desired_rpm)
            continue


        # -------------------------------------------------
        # 9 HARD STOP BELOW THRESHOLD
        # -------------------------------------------------
        if desired_rpm == 0 and current <= STOP_HARD_RPM_THRESHOLD:

            state.ramp_active = False
            set_rpm(0)
            continue


        # -------------------------------------------------
        # 10 FAST STOP ABOVE THRESHOLD
        # -------------------------------------------------
        if desired_rpm == 0 and current > STOP_HARD_RPM_THRESHOLD:

            if not state.ramp_active:
                state.ramp_active = True
                state.ramp_start_time = time.monotonic()
                state.ramp_start_rpm = current
                state.ramp_target_rpm = 0

            elapsed = time.monotonic() - state.ramp_start_time

            new_rpm = smoothstep(
                state.ramp_start_rpm,
                0,
                elapsed,
                STOP_RAMP_TIME
            )

            if elapsed >= STOP_RAMP_TIME:
                state.ramp_active = False
                new_rpm = 0

            set_rpm(new_rpm)
            continue

        # -------------------------------------------------
        # 11 NORMAL SMOOTHSTEP RAMP
        # -------------------------------------------------

        if abs(desired_rpm - current) > max(5, current * 0.02) and \
            ((not state.ramp_active) or abs(desired_rpm - state.ramp_target_rpm) > 15):

            state.ramp_active = True
            state.ramp_start_time = time.monotonic()
            state.ramp_start_rpm = current
            state.ramp_target_rpm = desired_rpm

        elapsed = time.monotonic() - state.ramp_start_time

        # -------------------------------------------------
        # 12 adaptive ramp duration based on speed
        # -------------------------------------------------

        ramp_time = RAMP_TIME
        if state.ramp_target_rpm > 300:
            ramp_time *= 0.6
        if state.ramp_target_rpm > 500:
            ramp_time *= 0.7

        new_rpm = smoothstep(
            state.ramp_start_rpm,
            state.ramp_target_rpm,
            elapsed,
            ramp_time
        )

        if elapsed >= RAMP_TIME:
            state.ramp_active = False
            new_rpm = state.ramp_target_rpm


        # -------------------------------------------------
        # 13 set speed based on new_rpm
        # -------------------------------------------------

        #print(
        #    "desired:", desired_rpm,
        #    "target:", state.target_rpm,
        #    "ramp_target:", state.ramp_target_rpm,
        #    "remaining:", state.remaining_turns
        # )

        set_rpm(new_rpm)
