# ============================================================
# Super Twister 3001
# Main window containing all UI elements and application logic
# Author: Andreas Reder
# ============================================================

# =========================
# Standard library imports
# =========================
import sys
import os
import time
import tkinter as tk
from tkinter import messagebox as mb
from tkinter import ttk

# =========================
# Third-party imports
# =========================
import customtkinter as ctk
from PIL import Image

# =========================
# Application imports
# =========================
import configs.language as language
import state
from configs.config import *
from hardware.reset import poll_reset
from hardware.motor import start_motor, stop_motor, start_centering, toggle_motor
from hardware.cpu_temp import cpu_temp
from ui.calibration_dialog import CalibrationDialog
from ui.login_popup import LoginPopup
from ui.recipe_dialog import RecipeDialog
from ui.config_editor import ConfigEditor
from ui.help_wizard import HelpDialog
from ui.help_twister import HelpTwisterDialog
from ui.statistic_dialog import StatisticDialog
from ui.rotating_image import RotatingGear

# =========================
# Global runtime state
# =========================
active_dialog = None         # Currently open modal dialog
_update_job = None           # Tkinter after() job reference

# Button press timing (used for acceleration)
press_time = 0.0
press_mtime = 0.0
press_cnt_time = 0.0
press_cnt_mtime = 0.0

# CPU temperature polling counter
cpu_temp_counter = 0

# ================ BUILD MAIN =================
def create_main_window():
    """
    Create and initialize the main application window,
    including layout, widgets, bindings and update loop.
    """

    # --------------------------------------------------------
    # INITIAL SETUP
    # --------------------------------------------------------
    active_dialog = None
    _update_job = None
    current_value = 0
    last_target = -1
    animating = False

    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")

    # ================= ROOT =================
    root = ctk.CTk()

    if FULLSCREEN:
        root.attributes("-fullscreen", True) # real fullscreen
    else:
        root.geometry(f"{width}x{height}")
    root.title(APP_NAME)
    root.config(cursor="none")  # mouse cursor off
    root.bind("<Escape>", lambda e: exit_app())

    # ================= GRID =================
    root.grid_columnconfigure(0, weight=1)
    root.grid_columnconfigure(1, weight=1)
    root.grid_columnconfigure(2, weight=0)
    root.grid_rowconfigure((0, 1, 2, 3), weight=1)

    # Initial CPU temp
    cpu_temp()

    # --------------------------------------------------------
    # UI COLOR DEFINITIONS
    # --------------------------------------------------------
    BG = "#1e1e1e"
    CARD = "#2b2b2b"
    BORDER = "#3a3a3a"
    BORDER_LIGHT = "#5a5a5a"

    FG_COLOR = "#444444"
    BUTTON = "#afafaf"

    TEXT_COLOR = "#f8f3f3"
    TEXT_DARK = "#000000"

    GREEN = "#2e7d32"
    RED = "#c62828"
    BLUE = "#1565c0"
    ORANGE = "#f9a825"
    YELLOW = "#c5a60a"
    GREY = "gray"

    TWIST_COLOR = "#fffb00"

    START_BORDER = "#035817"
    STOP_BORDER = "#8A0707"
    TWIST_BORDER = "#E28706"

    TRANSPARENT = "transparent"

    root.configure(fg_color=BG)

    # --------------------------------------------------------
    # UI HELPER FUNCTIONS
    # --------------------------------------------------------
    def card(parent, color=CARD, width=None, height=None):
        """
        Create a styled card-like frame used throughout the UI.
        Supports optional fixed width and height.
        """
        kwargs = {}
        if width is not None:
            kwargs["width"] = width
        if height is not None:
            kwargs["height"] = height

        return ctk.CTkFrame(
            parent,
            fg_color=color,
            corner_radius=15,
            border_width=5,
            border_color=BORDER,
            **kwargs
        )

    # ============================================================
    # LOGIC METHODS
    # ============================================================
    def open_modal(dialog_class, *args, **kwargs):
        nonlocal active_dialog

        if active_dialog and active_dialog.winfo_exists():
            active_dialog.lift()
            return

        dialog = dialog_class(root, *args, **kwargs)
        active_dialog = dialog
        dialog.transient(root)
        dialog.grab_set()
        dialog.focus_force()
        dialog.lift()

        def on_close():
            nonlocal active_dialog
            try:
                dialog.grab_release()
            except:
                pass
            dialog.destroy()
            active_dialog = None

        dialog.protocol("WM_DELETE_WINDOW", on_close)
    
    def gradient_color(percent: int) -> str:
        """
        0%   = Gruen
        50%  = Gelb
        100% = Rot
        """
        percent = max(0, min(100, percent))
        if percent <= 50:
            # Gruen -> Gelb
            r = int(255 * (percent / 50))
            g = 255
            b = 100 
        else:
            # Gelb -> Rot
            r = 255
            g = int(255 * (1 - (percent - 50) / 50))
            b = 100

        return f"#{r:02x}{g:02x}{b:02x}"

    def clamp(val, vmin, vmax):
        return max(vmin, min(vmax, val))

    def step_up(val, step):
        if val < step:
            return step
        return val + step

    def step_down(val, step):
        return val - step

    def on_plus_press(e):
        global press_time
        press_time = time.time()
        repeat_plus()

    def on_plus_release(e):
        global repeat_job
        if repeat_job:
            root.after_cancel(repeat_job)
            repeat_job = None

    def repeat_plus():
        """
        Continuously increase RPM while button is pressed.
        Uses acceleration after 1 second.
        """
        global repeat_job
        dt = time.time() - press_time
        step = FAST_STEP if dt > 1.0 else STEP_RPM
        new = step_up(state.target_rpm, step)
        state.target_rpm = clamp(new, MIN_RPM, MAX_RPM)
        repeat_job = root.after(200, repeat_plus)

    def on_minus_press(e):
        global press_mtime
        press_mtime = time.time()
        repeat_minus()
    
    def on_minus_release(e):
        global repeat_job
        if repeat_job:
            root.after_cancel(repeat_job)
            repeat_job = None

    def repeat_minus():
        global repeat_job
        dt = time.time() - press_mtime
        step = FAST_STEP if dt > 1.0 else STEP_RPM
        new = step_down(state.target_rpm, step)
        state.target_rpm = clamp(new, MIN_RPM, MAX_RPM)
        repeat_job = root.after(200, repeat_minus)

    def on_plus_cnt_press(e):
        if state.machine_state != IDLE:
            return
        global press_cnt_time
        press_cnt_time = time.time()
        repeat_cnt_plus()

    def on_plus_cnt_release(e):
        global repeat_job
        if repeat_job:
            root.after_cancel(repeat_job)
            repeat_job = None

    def repeat_cnt_plus():
        global repeat_job
        dt = time.time() - press_cnt_time
        step = STEP_RPM if dt > 1.0 else 1
        new = step_up(state.remaining_turns, step)
        state.remaining_turns = clamp(new, 0, MAX_TWIST)
        repeat_job = root.after(200, repeat_cnt_plus)

    def on_minus_cnt_press(e):
        if state.machine_state != IDLE:
            return
        global press_cnt_mtime
        press_cnt_mtime = time.time()
        repeat_cnt_minus()

    def on_minus_cnt_release(e):
        global repeat_job
        if repeat_job:
            root.after_cancel(repeat_job)
            repeat_job = None

    def repeat_cnt_minus():
        global repeat_job
        dt = time.time() - press_cnt_mtime
        step = STEP_RPM if dt > 1.0 else 1
        new = step_down(state.remaining_turns, step)
        state.remaining_turns = clamp(new, 0, MAX_TWIST)
        repeat_job = root.after(200, repeat_cnt_minus)

    def set_start_rpm(e=None):
        if e and state.machine_state != IDLE:
            return
        if state.target_rpm != START_RPM:
            state.toggle_rpm = state.target_rpm
            state.target_rpm = START_RPM
        else:
            state.target_rpm = state.toggle_rpm

    def set_endless(e=None):
        if e and state.machine_state != IDLE:
            return
        state.remaining_turns = 0
        state.endless_turns = 1
        toggle_counter(e)

    def toggle_counter(e=None):
        if e and state.machine_state != IDLE:
            return
        state.completed_turns = 0 if state.completed_turns > 0 else 0

    def toggle_lang():
        state.language = EN if state.language == DE else DE

    def toggle_reset(e=None):
        if getattr(state, "twist_mode", False):
            state.target_rpm = TWIST_RPM
            t = language.texts[state.language]
            mb.showinfo(t['info'], t['error_twist_mode'].format(TWIST_RPM=TWIST_RPM))
            return False
        else:
            state.target_rpm = state.loaded_rpm
        state.remaining_turns = state.loaded_turns
        state.completed_turns = 0
        if state.loaded_turns > 0:
            state.endless_turns = 0
            state.throttle_blocked = False
        return True

    def on_start():
        if state.machine_state != IDLE:
            return
        start_motor()

    def stop_button():
        state.motor_locked = False
        state.machine_state = IDLE
        stop_motor()

    def toggle_sec():
        state.safety_estop = False if state.safety_estop else False
        if not state.safety_estop:
            t = language.texts[state.language]
            stop_motor()
            mb.showinfo(t['exit'], t['exithint'])

    def toggle_twist():
        """
        Toggle between twist mode and normal serve mode.
        Adjusts target RPM accordingly.
        """
        state.twist_mode = True if not state.twist_mode else False
        if state.twist_mode:
            state.toggle_rpm = state.target_rpm
            state.target_rpm = TWIST_RPM
        else:
            state.target_rpm = state.toggle_rpm

    def toggle_calibration():
        state.machine_state = SAFE
        open_modal(CalibrationDialog)

    def stop_update_loop() -> None:
        global _update_job
        if _update_job is not None:
            try:
                root.after_cancel(_update_job)
            except Exception:
                pass
            _update_job = None

    def exit_app():
        stop_update_loop()
        root.after(100, restart_programm)

    def restart_programm():
        root.destroy()
        python = sys.executable
        os.execl(python, python, *sys.argv)

    after_id = None
    hint_visible = None

    def start_press(event):
        global after_id
        after_id = None
        if state.machine_state != IDLE:
            return
        if toggle_reset(event):
            after_id = root.after(700, lambda: show_hint(event))

    def end_press(event):
        global after_id, hint_visible
        if after_id:
            root.after_cancel(after_id)
            after_id = None
        if hint_visible:
            # Start timer to hide hint after 3 seconds
            root.after(3000, lambda: hide_hint())
        else:
            hint.place_forget()

    def hide_hint():
        global hint_visible
        hint.place_forget()
        hint_visible = False

    def show_hint(event):
        global hint_visible
        widget = event.widget
        x = widget.winfo_rootx() - 285
        y = widget.winfo_rooty() - root.winfo_rooty() + widget.winfo_height() + 50

        #hint.place(x=x, y=y)
        hint_visible = True

    def load_icon(name, color="white", size=(28, 28)):
        return ctk.CTkImage(
            light_image=Image.open(f"img/icons/{name}_{color}.png"),
            size=size
        )

    icon_play     = load_icon("forwd", "white")
    icon_stop     = load_icon("stopp", "white")
    icon_center   = load_icon("center", "white1")
    icon_serve_l  = load_icon("backward", "white", size=(42,42))
    icon_serve_r  = load_icon("forward", "white", size=(42,42))
    icon_twist    = load_icon("serve", "black", size=(42,42))
    icon_load     = load_icon("load", "white")
    icon_save     = load_icon("list", "white")
    icon_lang     = load_icon("lang", "white")
    icon_exit     = load_icon("exit", "white")
    icon_fairy    = load_icon("fairy", "white")
    icon_reset    = load_icon("reset", "white")
    icon_infinity = load_icon("infinity", "white")
    icon_cfg      = load_icon("config", "white", size=(42,42))
    icon_wzd      = load_icon("wizard", "white", size=(42,42))
    icon_hlp      = load_icon("help", "white")
    icon_trl      = load_icon("turtle", "white", size=(70,60))
    icon_rbt      = load_icon("rabbit", "white", size=(70,60))
    icon_service  = load_icon("security", "shield")
    icon_de       = load_icon("de", "white", size=(40,40))
    icon_en       = load_icon("en", "white", size=(40,40))
    icon_ok       = load_icon("ok", "green")
    icon_nok      = load_icon("nok", "rot")
    icon_unlock   = load_icon("unlock", "white", size=(40,40))

    root.protocol("WM_DELETE_WINDOW", exit_app)
    
    # ================= BUILD UI =================    

    # ============================================================
    # UI: RPM CONTROL PANEL
    # ============================================================
    frame_rpm = card(root, "black")
    frame_rpm.grid(row=0, column=0, rowspan=2, padx=10, pady=10, sticky="nsew")

    head_rpm = ctk.CTkLabel(frame_rpm, font=TARGET_FONT)
    head_rpm.pack(pady=(10,0))

    val_rpm = ctk.CTkLabel(frame_rpm, font=BIG_BIG_FONT)
    val_rpm.pack()

    lbl_rpm = ctk.CTkLabel(frame_rpm, font=LBL_FONT)
    lbl_rpm.pack()

    btn_row = ctk.CTkFrame(frame_rpm, fg_color=TRANSPARENT)
    btn_row.pack(pady=10)

    btn_minus = ctk.CTkButton(btn_row, text="-", font=BIG_FONT_MINUS, height=65, width=70, bg_color=CARD)
    btn_minus.grid(row=0, column=0, padx=5)

    btn_turtle = ctk.CTkButton(btn_row, text="", height=65, width=70, image=icon_trl, compound="left")
    btn_turtle.grid(row=0, column=1, padx=5)

    btn_plus = ctk.CTkButton(btn_row, text="+", font=BIG_FONT_MINUS, height=65, width=70, bg_color=CARD)
    btn_plus.grid(row=0, column=2, padx=5)

    # ============================================================
    # UI: TURN COUNTER PANEL
    # ============================================================
    frame_target = card(root, "black")
    frame_target.grid(row=0, column=1, rowspan=2, padx=10, pady=10, sticky="nsew")

    head_cnt = ctk.CTkLabel(frame_target, font=TARGET_FONT)
    head_cnt.pack(pady=(10,0))

    val_cnt = ctk.CTkLabel(frame_target, font=BIG_FONT_MINUS)
    val_cnt.pack()

    lbl_cnt = ctk.CTkLabel(frame_target, font=LBL_FONT)
    lbl_cnt.pack()

    btn_cnt_row = ctk.CTkFrame(frame_target, fg_color="transparent")
    btn_cnt_row.pack(pady=10)

    btn_cnt_minus = ctk.CTkButton(btn_cnt_row, text="-", font=BIG_FONT_MINUS, width=70, command=lambda: (
        setattr(state, "remaining_turns", max(0, state.remaining_turns)),
        setattr(state, "endless_turns", 1 if state.remaining_turns <= 1 else 0)))
    btn_cnt_minus.grid(row=0, column=0, padx=5)

    btn_inf = ctk.CTkButton(btn_cnt_row, text="", height=65, width=70, image=icon_infinity, compound="left")
    btn_inf.grid(row=0, column=1, padx=5)

    btn_cnt_plus = ctk.CTkButton(btn_cnt_row, text="+", font=BIG_FONT_MINUS, width=70, command=lambda: (
        setattr(state, "remaining_turns", max(0, state.remaining_turns)),
        setattr(state, "endless_turns", 0)))
    btn_cnt_plus.grid(row=0, column=2, padx=5)

    # ============================================================
    # UI: RIGHT SIDEBAR (CONFIG + SYSTEM)
    # ============================================================
    
    # ================= RECEIPE (Config) =================
    frame_conf = card(root, CARD, width=280)
    frame_conf.grid(row=0, column=2, rowspan=2, padx=10, pady=10, sticky="ns")
    frame_conf.grid_propagate(False)

    ctk.CTkLabel(frame_conf, text="Konfiguration", font=LBL_FONT).pack(pady=5)

    btn_lcfg = ctk.CTkButton(frame_conf, text="Load", font=BUTTON_FONT, fg_color=FG_COLOR, text_color=TEXT_COLOR, image=icon_load, height=50, width=250)
    btn_lcfg.pack(fill="x", padx=10, pady=5)

    btn_scfg = ctk.CTkButton(frame_conf, text="Save", font=BUTTON_FONT, fg_color=FG_COLOR, text_color=TEXT_COLOR, image=icon_save, height=50, width=250)
    btn_scfg.pack(fill="x", padx=10, pady=5)

    lbl_lcfg = ctk.CTkButton(frame_conf, font=LBL_FONT, fg_color=BUTTON, text_color=BG, width = 12)
    lbl_lcfg.pack(fill="x", padx=10, pady=5)
    lbl_lcfg.bind("<ButtonPress-1>", start_press)
    lbl_lcfg.bind("<ButtonRelease-1>", end_press)

    hint = ctk.CTkLabel(root, text="Hint", font=LBL_FONT, padx=PAD_X, pady=PAD_Y)

    # ================= SYSTEM =================
    frame_sys = card(root, CARD, width=280)
    frame_sys.grid(row=2, column=2, rowspan=3, padx=10, pady=10, sticky="ns")
    frame_sys.grid_propagate(False)

    ctk.CTkLabel(frame_sys, text="System", font=LBL_FONT).pack(pady=10)

    btn_lang = ctk.CTkButton(frame_sys, font=BIG_FONT, fg_color=FG_COLOR, text_color=TEXT_COLOR,
                        image=icon_lang, anchor="w", compound="left", height=50, width=250)
    btn_lang.pack(fill="x", padx=10, pady=5)

    btn_help = ctk.CTkButton(frame_sys, font=BIG_FONT, fg_color=FG_COLOR, text_color=TEXT_COLOR,
                        image=icon_hlp, anchor="w", compound="left", height=50, width=250)
    btn_help.pack(fill="x", padx=10, pady=5)

    btn_service = ctk.CTkButton(frame_sys, font=BIG_FONT, fg_color=FG_COLOR, text_color=TEXT_COLOR,
                        image=icon_unlock, anchor="w", compound="left", height=50, width=250)
    btn_service.pack(fill="x", padx=10, pady=5)

    # ============================================================
    # UI: STATUS AREA
    # ============================================================
    frame_status = card(root)
    frame_status.grid(row=2, column=0, columnspan=2, padx=10, pady=1, sticky="ew")

    frame_status.grid_columnconfigure(0, weight=1)
    frame_status.grid_columnconfigure(1, weight=0)

    # ---------- TEXT LINKS ----------
    lbl_state = ctk.CTkLabel(
        frame_status,
        text="",
        font=LBL_FONT,
        image=icon_service,
        compound="left",
        anchor="w",
        height=55,
        padx=10
    )
    lbl_state.grid(row=0, column=0, padx=20, pady=10, sticky="w")

    # ---------- THROTTLE RECHTS ----------
    bar_frame = ctk.CTkFrame(frame_status, fg_color="transparent")
    bar_frame.grid(row=0, column=1, padx=20, pady=10, sticky="e")

    throttle = ctk.CTkProgressBar(
        bar_frame,
        width=180,
        height=38,
        corner_radius=19
    )
    throttle.set(0)
    throttle.pack()
    throttle.configure(border_width=5, border_color=BORDER)

    # Prozent-Anzeige
    percent_label = ctk.CTkLabel(
        throttle,
        text="0 %",
        font=PROGRESS_FONT,
        fg_color="transparent",
        text_color="white"
    )
    percent_label.place(relx=0.5, rely=0.5, anchor="center")

    # ============================================================
    # UI: MAIN ACTION BUTTONS
    # ============================================================
    frame_actions = ctk.CTkFrame(root, fg_color="transparent")
    frame_actions.grid(row=3, column=0, columnspan=2, padx=10, pady=5, sticky="nsew")

    frame_actions.grid_columnconfigure((0,1), weight=1)

    btn_start = ctk.CTkButton(frame_actions, text="Start", command=on_start, font=BIG_FONT_MINUS, image=icon_play, corner_radius=15, fg_color=GREEN, height=85, border_width=6, border_color=START_BORDER, text_color=TEXT_COLOR)
    btn_start.grid(row=0, column=0, padx=5, sticky="ew")

    btn_stop = ctk.CTkButton(frame_actions, text="Stop", command=stop_button, font=BIG_FONT_MINUS, image=icon_stop, corner_radius=15, fg_color=RED, height=85, border_width=6, border_color=STOP_BORDER, text_color=TEXT_COLOR)
    btn_stop.grid(row=0, column=1, padx=5, sticky="ew")

    # ================= CENTER ACTION =================
    frame_center = card(root, "black")
    frame_center.configure(height=65)
    frame_center.grid_propagate(False)
    frame_center.grid(row=4, column=0, columnspan=2, padx=10, pady=5, sticky="nsew")
    frame_center.grid_columnconfigure((0,1,2), weight=1)
    frame_center.grid_rowconfigure(0, weight=1)

    btn_ri = ctk.CTkButton(frame_center, text="↻", font=BIG_BIG_FONT, command=lambda: setattr(state, "direction", True))
    btn_ri.grid(row=0, column=0, sticky="w", padx=(10,0))

    btn_center = ctk.CTkButton(frame_center, command=start_centering, image=icon_center, font=BUTTON_FONT_BOLD, fg_color=BLUE)
    btn_center.grid(row=0, column=1, padx=5, sticky="ew")

    btn_le = ctk.CTkButton(frame_center, text="↺", font=BIG_BIG_FONT, command=lambda: setattr(state, "direction", False))
    btn_le.grid(row=0, column=2, sticky="e", padx=(0,10))

    # ================= MAIN ACTION =================
    frame_main = ctk.CTkFrame(root, fg_color="transparent")
    frame_main.grid(row=5, column=0, columnspan=3, padx=10, pady=5, sticky="nsew")
    frame_main.grid_columnconfigure(0, weight=0)
    frame_main.grid_columnconfigure(1, weight=0)
    frame_main.grid_columnconfigure(2, weight=2)
    frame_main.grid_columnconfigure(3, weight=1)

    btn_wzd = ctk.CTkButton(frame_main, text="Wizard", font=LBL_FONT,
                        image=icon_wzd, compound="top", fg_color=FG_COLOR, text_color=TEXT_COLOR)
    btn_wzd.grid(row=0, column=0, sticky="nsew", padx=(0,5))

    btn_config = ctk.CTkButton(frame_main, text="Config", font=LBL_FONT,
                        image=icon_cfg, compound="top", fg_color=FG_COLOR, text_color=TEXT_COLOR)
    btn_config.grid(row=0, column=1, sticky="nsew", padx=(5,0))
 
    btn_twist = ctk.CTkButton(
        frame_main,
        text="TWIST" if state.twist_mode else "SERVE",
        fg_color=ORANGE,
        image=icon_center,
        command=toggle_twist,
        width=350,
        height=75,
        font=BIG_FONT,
        corner_radius=15, border_width=6, border_color=TWIST_BORDER, text_color=TEXT_COLOR
    )
    btn_twist.grid(row=0, column=2, columnspan=1, padx=(40,10), pady=10, sticky="ew")

    # ================= INFO GRID =================

    frame_info = card(frame_main)
    frame_info.grid(row=0, column=3, padx=10, pady=5, sticky="ne")
    frame_info.grid_propagate(False)

    # Innenabstand simulieren (wie Padding im Screenshot)
    inner = ctk.CTkFrame(frame_info, fg_color="transparent")
    inner.pack(fill="both", expand=True, padx=6, pady=6)


    # Grid structure
    inner.grid_columnconfigure(0, weight=0)
    inner.grid_rowconfigure(0, weight=1)
    inner.grid_rowconfigure(1, weight=1)


    # --- language (on top)
    lbl_lang = ctk.CTkLabel(
        inner,
        text="Sprache",
        image=icon_de if state.language == DE else icon_en,
        compound="left",
        font=TARGET_FONT,
        text_color=TEXT_COLOR
    )
    lbl_lang.grid(row=0, column=0, sticky="we", pady=(10, 5))


    # --- lower line
    bottom = ctk.CTkFrame(inner, fg_color="transparent")
    bottom.grid(row=1, column=0, sticky="ew")

    bottom.grid_columnconfigure(0, weight=1)
    bottom.grid_columnconfigure(1, weight=0)


    # CPU Temp. (left)
    temp_label = ctk.CTkLabel(
        bottom,
        text=f"CPU: {state.cpu_temp} °C",
        font=SVC_FONT,
        text_color=TEXT_COLOR
    )
    temp_label.grid(row=0, column=0, padx=(10, 0), sticky="w")

    # Exit Button (right)
    btn_quit = ctk.CTkButton(
        bottom,
        text="Exit",
        image=icon_exit,
        compound="left",
        width=140,
        height=32,
        corner_radius=12,
        fg_color=BORDER,
        text_color=TEXT_COLOR
    )
    btn_quit.grid(row=0, column=1, padx=(10, 0), pady=(4, 0), sticky="e")
   
    # ================= ANIMATION =================
    def animate_press(btn, color):
        btn.bind("<ButtonPress-1>", lambda e: btn.configure(fg_color=FG_COLOR))
        btn.bind("<ButtonRelease-1>", lambda e: btn.configure(fg_color=color))

    animate_press(btn_start, GREEN)
    animate_press(btn_stop, RED)
    animate_press(btn_center, BLUE)
    animate_press(btn_twist, ORANGE)

    # --------------------------------------------------------
    # EVENT BINDINGS
    # --------------------------------------------------------
    btn_plus.bind("<ButtonPress-1>", on_plus_press)
    btn_plus.bind("<ButtonRelease-1>", on_plus_release)

    btn_minus.bind("<ButtonPress-1>", on_minus_press)
    btn_minus.bind("<ButtonRelease-1>", on_minus_release)

    btn_turtle.bind("<Button-1>", set_start_rpm)
    #lock_lbl.bind("<Button-1>", lambda e: toggle_motor() if state.machine_state == IDLE else None)
    lbl_state.bind("<Button-1>", lambda e: toggle_sec() if state.machine_state == IDLE else None)

    btn_cnt_plus.bind("<ButtonPress-1>", on_plus_cnt_press)
    btn_cnt_plus.bind("<ButtonRelease-1>", on_plus_cnt_release)

    btn_cnt_minus.bind("<ButtonPress-1>", on_minus_cnt_press)
    btn_cnt_minus.bind("<ButtonRelease-1>", on_minus_cnt_release)

    #btn_inf.bind("<Button-1>", set_endless)
    lbl_cnt.bind("<Button-1>", toggle_counter)

    # --- configure buttons

    btn_inf.configure(command=set_endless)

    btn_start.configure(command=on_start)
    btn_center.configure(command=start_centering)
    btn_stop.configure(command=stop_button)

    btn_lang.configure(command=toggle_lang)
    btn_service.configure(command=lambda: open_modal(LoginPopup))
    btn_quit.configure(command=exit_app)

    btn_lcfg.configure(command=lambda: open_modal(RecipeDialog, mode="load"))
    btn_lcfg.bind("<ButtonPress-1>", start_press)
    btn_lcfg.bind("<ButtonRelease-1>", end_press)

    btn_scfg.configure(command=lambda: open_modal(RecipeDialog, mode="save"))

    btn_wzd.configure(command=lambda: open_modal(HelpDialog))

    btn_config.configure(command=lambda: open_modal(HelpTwisterDialog))

    btn_ri.configure(command=lambda: setattr(state, "direction", True))
    btn_le.configure(command=lambda: setattr(state, "direction", False))

    btn_help.configure(command=lambda: open_modal(HelpTwisterDialog))
    
    btn_twist.configure(command=toggle_twist)

    frame_sys.configure(width=300)
    frame_conf.configure(width=300)

    frame_info.configure(corner_radius=15)
    frame_info.configure(width=300)
    btn_quit.configure(corner_radius=10)
    lbl_lang.configure(padx=5)
    btn_quit.configure(border_width=3, border_color=BORDER_LIGHT)
    lbl_lcfg.configure(text=f"\u2139 {state.current_profile}", font=LBL_FONT, anchor="w")

    # ================= UPDATE LOOP =================
    # ------ loop to update  windows variables ------
    # ===============================================
    def update():
        nonlocal _update_job
        nonlocal temp_label
        global cpu_temp_counter
        
        cpu_temp_counter += 1
        if cpu_temp_counter >= 100:  # 10 seconds at 100ms
            cpu_temp()
            cpu_temp_counter = 0
            temp_label.configure(text=f"CPU: {state.cpu_temp} °C")
            if isinstance(state.cpu_temp, (int, float)) and state.cpu_temp > ALERT_CPU_TEMP:
                temp_label.configure(fg_color="red", font=SVC_FONT_BOLD)
            else:
                temp_label.configure(fg_color="transparent", font=SVC_FONT_BOLD)
                
        t = language.texts[state.language]
        is_safe = state.machine_state == SAFE
        is_running = state.machine_state == RUNNING
        is_idle = state.machine_state == IDLE
        head_rpm.configure(text=f"{t['rpm']}")
        lbl_rpm.configure(text=f"{t['head_rpm']}")
        val_rpm.configure(text=f"{int(state.actual_rpm)} / {int(state.target_rpm)}")

        if state.remaining_turns == 0:
            val_cnt.configure(text="∞", font=BIG_BIG_FONT)
            btn_cnt_plus.configure(state=DISABLED if is_running else NORMAL)
            btn_cnt_minus.configure(state=DISABLED if is_running else NORMAL)
        else:
            val_cnt.configure(
                text=f"{int(state.remaining_turns)}",
                font=BIG_BIG_FONT
            )
        head_cnt.configure(text=f"{t['counts']}")
        lbl_cnt.configure(text=f"{t['counter']} {int(state.completed_turns)}")
        lbl_state.configure(
            text=f"{t['state']}: "
                f"{state.machine_state}"
                f"{' ' + (t['cw'] if state.direction else t['ccw']) if state.machine_state == RUNNING else ''} "
                f"({state.user_role})"
        )
        lbl_state.configure(image=icon_ok 
                            if not state.error 
                            and not state.safety_estop 
                            and not state.machine_state == "SAFE"
                            and not state.machine_state == "ERROR"
                            else icon_nok)
        btn_inf.configure(image=icon_reset if state.remaining_turns == 0 else icon_infinity)

        #gear = RotatingGear(btn_cnt_row, "img/icons/reset_white.png", size=60, speed=5)
        #gear.grid(row=0, column=1, padx=5)

        btn_start.configure(text=t["start"])
        btn_center.configure(text=t["center"])
        btn_stop.configure(text=t["stop"])
        btn_lang.configure(text=f"{t['language']} {state.language}")
        lbl_lang.configure(text=f"{t['language']}", image=icon_de if state.language == "DE" else icon_en)
        btn_lcfg.configure(text=f"Load {t['config']}")
        btn_scfg.configure(text=f"Save {t['config']}")
        hint.configure(text=f"{t['loaded_recipe']}:\n" f"{state.current_profile}", font=LBL_FONT)
        btn_wzd.configure(text=t["wizard"])
        btn_help.configure(text= f"{t['help']}")
        btn_service.configure(text=t["service"], fg_color=YELLOW if state.user_role == SERVICE or state.user_role == CALIBRATION or state.user_role == STATISTIC else FG_COLOR)
        if state.user_role == CALIBRATION:
            btn_config.configure(text=t["calibration"], fg_color=YELLOW if state.user_role == CALIBRATION else FG_COLOR, command=toggle_calibration)
        elif state.user_role == STATISTIC:
            btn_config.configure(text=t["statistic"], fg_color=YELLOW if state.user_role == STATISTIC else FG_COLOR, command=lambda: open_modal(StatisticDialog))
        else:
            btn_config.configure(text=t["configuration"], fg_color=YELLOW if state.user_role == SERVICE else FG_COLOR, command=lambda: open_modal(ConfigEditor))
            
        btn_ri.configure(fg_color = GREEN if state.direction else GREY)
        btn_le.configure(fg_color= GREEN if state.direction == False else GREY)
        
        if state.twist_mode:
            twist = icon_twist    
        else:
            if state.direction:
                twist = icon_serve_r
            else:
                twist = icon_serve_l     
        btn_twist.configure(text=t["twist"] if state.twist_mode else t["serve"],
                            fg_color=TWIST_COLOR if state.twist_mode else ORANGE,
                            text_color=TEXT_DARK if state.twist_mode else TEXT_COLOR,
                            image=twist)
        
        btn_turtle.configure(image=icon_trl if state.target_rpm == START_RPM else icon_rbt)

        # --- block buttons for use ---
        btn_stop.configure(state=NORMAL if not is_idle else DISABLED)
        btn_start.configure(state=NORMAL if is_idle else DISABLED)
        btn_center.configure(state=NORMAL if is_idle else DISABLED)
        btn_quit.configure(state=NORMAL if is_idle else DISABLED)
        btn_lang.configure(state=NORMAL if is_idle else DISABLED)
        btn_lcfg.configure(state=NORMAL if is_idle else DISABLED)
        btn_scfg.configure(state=NORMAL if is_idle else DISABLED)
        btn_service.configure(state=NORMAL if is_idle or is_safe else DISABLED)
        btn_config.configure(state=NORMAL if is_idle or is_safe else DISABLED)
        btn_ri.configure(state=NORMAL if is_idle else DISABLED)
        btn_le.configure(state=NORMAL if is_idle else DISABLED)
        btn_twist.configure(state=NORMAL if is_idle else DISABLED)
        btn_help.configure(state=NORMAL if is_idle else DISABLED)
        btn_wzd.configure(state=NORMAL if is_idle else DISABLED)
        btn_cnt_plus.configure(state=NORMAL if is_idle else DISABLED)
        btn_cnt_minus.configure(state=NORMAL if is_idle else DISABLED)
        lbl_lcfg.configure(state=NORMAL if is_idle else DISABLED)

        # update throttle bar
        throttle_active = state.throttle_percent > THROTTLE_START
        if not throttle_active:
            percent = int(state.actual_rpm / state.target_rpm * 100) if state.target_rpm > 0 else 0
        else:
            percent = int(state.throttle_percent * 100)

        # color change, depend of throttle percent
        color_bar = gradient_color(percent)
        throttle.configure(progress_color=color_bar)
        throttle.set(percent / 100)

        percent_label.configure(text=f"{int(percent)} %")
        percent_label.configure(text_color=TEXT_DARK if percent > 60 else TEXT_COLOR)
        percent_label.configure(fg_color=BORDER_LIGHT if percent < 50 else color_bar)
        
        if root.winfo_exists():
            _update_job = root.after(UPDATE_MS, update)
        else:
            _update_job = None
        
    update()

    root.mainloop()