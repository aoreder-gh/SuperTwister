# ==============================================================
# Super Twister 3001
# main window with all ui elements and logic
# @author    Andreas Reder <aoreder@gmail.com>
# ==============================================================  

import sys, os
import time
import tkinter as tk
from tkinter import messagebox as mb
from tkinter import ttk

from PIL import ImageTk, Image

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

# ================= STATE =================
active_dialog = None
_update_job = None
press_time = 0.0
press_mtime = 0.0
press_cnt_time = 0.0
press_cnt_mtime = 0.0
cpu_temp_counter = 0

# ================ BUILD MAIN =================
def create_main_window():
    # ================= STATE =================
    active_dialog = None
    _update_job = None
    
    # ================= ROOT =================
    root = tk.Tk()
    root.tk.call('tk', 'scaling', 1.3)
    if FULLSCREEN == True:
        root.attributes("-fullscreen", True) # real fullscreen
    else:
        root.geometry(f"{width}x{height}")
    root.configure(bg="black")
    root.title(APP_NAME)
    root.config(cursor="none")  # mouse cursor off
    root.bind("<Escape>", lambda e: exit_app())

    # Initial CPU temp
    cpu_temp()

    # ================= BACKGROUND =================
    img = Image.open(IMG_PATH + 'archery-wallpaper-1.jpg')
    img = img.resize((width, height), 1)
    image1 = ImageTk.PhotoImage(img)
    
    # root has no image argument, so use a label as a panel
    panel1 = tk.Label(root, image=image1)
    panel1.pack(side="top", fill="both", expand=True)

    # style for progress bar
    style = ttk.Style()
    style.theme_use("default")

    # id for after job to show hint when long press on reset button
    after_id = None

    # ================= GRID =================
    #for c in range(7): panel1.columnconfigure(c, weight=1)
    for c in range(7):
        if c in (4, 5):
            panel1.columnconfigure(c, weight=0, minsize=80) # fix width in pixel
        else:
            panel1.columnconfigure(c, weight=1)
        if c in (3, 6):
            panel1.columnconfigure(c, weight=0, minsize=120)  # fix width in pixel
        else:
            panel1.columnconfigure(c, weight=1)

    for r in range(4): panel1.rowconfigure(r, weight=1)
    
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

    def rpm_plus():
        new = step_up(state.target_rpm, STEP_RPM)
        state.target_rpm = clamp(new, MIN_RPM, MAX_RPM)
        state.ramp_active = False

    def rpm_minus():
        new = step_down(state.target_rpm, STEP_RPM)
        state.target_rpm = clamp(new, MIN_RPM, MAX_RPM)
        state.ramp_active = False

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
        state.target_rpm = START_RPM

    def set_endless(e=None):
        state.remaining_turns = 0
        state.endless_turns = 1

    def toggle_counter(e=None):
        state.completed_turns = 0 if state.completed_turns > 0 else 0

    def toggle_lang():
        state.language = EN if state.language == DE else DE

    def toggle_reset(e=None):
        state.target_rpm = state.loaded_rpm
        state.remaining_turns = state.loaded_turns
        state.completed_turns = 0
        if state.loaded_turns > 0:
            state.endless_turns = 0
            state.throttle_blocked = False

    def on_start():
        if state.machine_state != IDLE:
            return
        start_motor()

    def stop_button():
        state.motor_locked = False
        state.machine_state = IDLE
        stop_motor()

    def toggle_sec():
        state.safety_estop = False if state.safety_estop == True else False
        if not state.safety_estop:
            t = language.texts[state.language]
            stop_motor()
            mb.showinfo(t['exit'], t['exithint'])

    def toggle_twist():
        state.twist_mode = True if state.twist_mode == False else False
        if state.twist_mode:
            #state.remaining_turns = 0
            #state.endless_turns = 1
            #state.throttle_blocked = False
            state.target_rpm = TWIST_RPM
        else:
            state.target_rpm = START_RPM

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

    def start_press(event):
        global after_id
        toggle_reset(event)
        after_id = root.after(700, lambda: show_hint(event))

    def end_press(event):
        global after_id
        if after_id:
            root.after_cancel(after_id)
            after_id = None
        hint.place_forget()

    def show_hint(event):
        widget = event.widget
        x = widget.winfo_rootx() - 500 # panel1.winfo_rootx()
        y = widget.winfo_rooty() - panel1.winfo_rooty() + widget.winfo_height()

        hint.place(x=x, y=y)


    root.protocol("WM_DELETE_WINDOW", exit_app)
    
    # ================= BUILD UI =================    

    # ### row 0 and 1 ###

    # --- RPM 0 ---
    btn_plus = tk.Button(panel1, text="+", font=BIG_FONT, bg="bisque2", activebackground="bisque2", borderwidth=5, relief="raised")
    btn_plus.grid(row=0, column=0, sticky="nse", padx=PAD_X, pady=PAD_Y)
    btn_plus.bind("<ButtonPress-1>", on_plus_press)
    btn_plus.bind("<ButtonRelease-1>", on_plus_release)

    # --- minus ---
    btn_minus = tk.Button(panel1, text="-", font=BIG_FONT_MINUS, bg="bisque2", activebackground="bisque2", borderwidth=5, relief="raised")
    btn_minus.grid(row=1, column=0, sticky="nse", padx=PAD_X, pady=PAD_Y)
    btn_minus.bind("<ButtonPress-1>", on_minus_press)
    btn_minus.bind("<ButtonRelease-1>", on_minus_release)

    # --- RPM and progress bar (same "position": column 1, split vertically) ---
    exit_rpm_frame = tk.Frame(panel1, bg="bisque2")
    exit_rpm_frame.grid(row=0, column=1, sticky="nsew", padx=PAD_X, pady=PAD_Y)

    exit_rpm_frame.rowconfigure(0, weight=1)
    exit_rpm_frame.rowconfigure(1, weight=1)
    exit_rpm_frame.columnconfigure(0, weight=1, minsize=120)

    # --- label RPM 1 ---
    lbl_rpm = tk.Label(exit_rpm_frame, font=BIG_FONT, bg=exit_rpm_frame.cget("bg"), borderwidth=5, relief="raised")
    lbl_rpm.grid(row=0, column=0, sticky="nsew", padx=PAD_X, pady=PAD_Y)
    lbl_rpm.bind("<Button-1>", set_start_rpm)
    
    # ---------- GAS PROGRESSBAR ----------
    bar_frame = tk.Frame(exit_rpm_frame, bg=exit_rpm_frame.cget("bg"), width=100, height=45)
    bar_frame.grid(row=1, column=0, sticky="nsew", padx=(PAD_X + 25), pady=PAD_Y)
    bar_frame.grid_propagate(False)
    bar_frame.rowconfigure(0, weight=1)
    bar_frame.columnconfigure(0, weight=1)

    style.configure(
        "Custom.Horizontal.TProgressbar",
        thickness=40,
        troughcolor="black"
    )

    throttle_bar = ttk.Progressbar(
        bar_frame,
        style="Custom.Horizontal.TProgressbar",
        orient="horizontal",
        mode="determinate",
        maximum=100
    )
    throttle_bar.grid(row=0, column=0, sticky="nsew")

    # Prozent mittig über Bar
    percent_label = tk.Label(
        bar_frame,
        text="0 %",
        font=("Arial", 18, "bold"),
        bg=bar_frame.cget("bg"),
        fg="black"
    )
    percent_label.place(relx=0.5, rely=0.75, anchor="s")

    # --- lock label 2 ---
    lock_lbl = tk.Label(panel1, font=LBL_FONT, borderwidth=5, relief="raised")
    lock_lbl.grid(row=0, column=2, sticky="nsew", padx=PAD_X, pady=PAD_Y)
    lock_lbl.bind("<Button-1>", toggle_motor)
    
    # --- label rpm 2 ---
    val_rpm = tk.Label(panel1, font=BIG_FONT, bg="medium purple")
    val_rpm.grid(row=1, column=1, sticky="nsew", padx=PAD_X, pady=PAD_Y)

    # --- label status 2 ---
    lbl_state = tk.Label(panel1, font=LBL_FONT, bg="medium purple", borderwidth=5, relief="raised")
    lbl_state.grid(row=1, column=2, sticky="nsew", padx=PAD_X, pady=PAD_Y)
    lbl_state.bind("<Button-1>", lambda e: toggle_sec())

    # --- Counter / Endless 3 ---
    btn_plus_cnt = tk.Button(panel1, text="+", font=BIG_FONT, bg="khaki1", borderwidth=5, relief="raised", command=lambda: (
        setattr(state, "remaining_turns", max(0, state.remaining_turns)),
        setattr(state, "endless_turns", 0)
    )
              )
    btn_plus_cnt.grid(row=0, column=3, sticky="nse", padx=PAD_X, pady=PAD_Y)
    btn_plus_cnt.bind("<ButtonPress-1>", on_plus_cnt_press)
    btn_plus_cnt.bind("<ButtonRelease-1>", on_plus_cnt_release)

    btn_minus_cnt = tk.Button(panel1, text="-", font=BIG_FONT_MINUS, bg="khaki1", borderwidth=5, relief="raised", command=lambda: (
        setattr(state, "remaining_turns", max(0, state.remaining_turns)),
        setattr(state, "endless_turns", 1 if state.remaining_turns <= 1 else 0)
    )
              )
    btn_minus_cnt.grid(row=1, column=3, sticky="nse", padx=PAD_X, pady=PAD_Y)
    btn_minus_cnt.bind("<ButtonPress-1>", on_minus_cnt_press)
    btn_minus_cnt.bind("<ButtonRelease-1>", on_minus_cnt_release)

    # --- Adj counter 4---
    lbl_cnt = tk.Label(panel1, bg="khaki1", borderwidth=5, relief="raised")
    lbl_cnt.grid(row=0, column=4, columnspan=2, sticky="nsew", padx=PAD_X, pady=PAD_Y)
    lbl_cnt.bind("<Button-1>", set_endless)

    val_cnt = tk.Label(panel1, font=BIG_BIG_FONT, borderwidth=5, relief="raised")
    val_cnt.grid(row=1, column=4, columnspan=2, sticky="nsew", padx=PAD_X, pady=PAD_Y)
    val_cnt.bind("<Button-1>", toggle_counter)

    # --- language and exit (same "position": column 6, split vertically) ---
    exit_lang_frame = tk.Frame(panel1, bg=panel1.cget("bg"))
    exit_lang_frame.grid(row=0, column=6, sticky="nsew", padx=PAD_X, pady=PAD_Y)

    exit_lang_frame.rowconfigure(0, weight=1)
    exit_lang_frame.rowconfigure(1, weight=1)
    exit_lang_frame.columnconfigure(0, weight=1)

    btn_quit = tk.Button(exit_lang_frame, text="EXIT", font=LBL_FONT, bg="gray35", fg="white", command=exit_app, borderwidth=5, relief="raised")
    btn_quit.grid(row=0, column=0, sticky="nsew")

    btn_lang = tk.Button(exit_lang_frame, font=LBL_FONT, command=toggle_lang, borderwidth=5, relief="raised")
    btn_lang.grid(row=1, column=0, sticky="nsew")

    # --- config load / current profile / config save (same "position": row=1, col=6, split vertically) ---
    cfg_frame = tk.Frame(panel1, bg=panel1.cget("bg"))
    cfg_frame.grid(row=1, column=6, sticky="nsew", padx=PAD_X, pady=PAD_Y)

    cfg_frame.rowconfigure(0, weight=1)
    cfg_frame.rowconfigure(1, weight=1)
    cfg_frame.rowconfigure(2, weight=1)
    cfg_frame.columnconfigure(0, weight=1)

    btn_lcfg = tk.Button(cfg_frame, font=LBL_FONT, borderwidth=5, relief="raised", command=lambda: open_modal(RecipeDialog, mode="load"))
    btn_lcfg.grid(row=0, column=0, sticky="nsew")

    lbl_lcfg = tk.Button(cfg_frame, font=LBL_FONT, bg="white", width = 12, borderwidth=5, relief="raised")
    hint = tk.Label(panel1, text="Hinweis", bg="light yellow", font=LBL_FONT, padx=PAD_X, pady=PAD_Y, borderwidth=5, relief="raised")
    lbl_lcfg.grid(row=1, column=0, sticky="nsew")
    #lbl_lcfg.bind("<Button-1>", toggle_reset)
    lbl_lcfg.bind("<ButtonPress-1>", start_press)
    lbl_lcfg.bind("<ButtonRelease-1>", end_press)

    btn_scfg = tk.Button(cfg_frame, font=LBL_FONT, borderwidth=5, relief="raised", command=lambda: open_modal(RecipeDialog, mode="save"))
    btn_scfg.grid(row=2, column=0, sticky="nsew")

    # ### row 2 ###

    # --- actions start - stop 2 ---
    btn_start = tk.Button(panel1, font=BIG_FONT, bg="green", activebackground="lightgreen", activeforeground="black", borderwidth=5, relief="raised",
                          command=on_start)
    btn_start.grid(row=2, column=0, columnspan=3, sticky="nsew", padx=PAD_X, pady=PAD_Y)

    btn_center = tk.Button(panel1, font=LBL_FONT, bg="blue", fg="white", activebackground="lightblue", activeforeground="white", borderwidth=5, relief="raised",
                           command=start_centering)
    btn_center.grid(row=2, column=3, columnspan=1, sticky="ns", padx=PAD_X, pady=PAD_Y)

    btn_stop = tk.Button(panel1, font=BIG_FONT, bg="red", activebackground="#F34F6B", activeforeground="black", borderwidth=5, relief="raised",
                         command=stop_button)
    btn_stop.grid(row=2, column=4, columnspan=3, sticky="nsew", padx=PAD_X, pady=PAD_Y)

    # ### row 3 ###

    # --- Wizzard + Twister Help  (same "position": row=3, col=0, split vertically) ---
    wzd_hlp_frame = tk.Frame(panel1, bg=panel1.cget("bg"))
    wzd_hlp_frame.grid(row=3, column=0, sticky="nsew", padx=PAD_X, pady=PAD_Y)

    wzd_hlp_frame.rowconfigure(0, weight=1)
    wzd_hlp_frame.rowconfigure(1, weight=1)        
    wzd_hlp_frame.columnconfigure(0, weight=1)

    # --- helper area 0 ---
    btn_wzd = tk.Button(wzd_hlp_frame, font=LBL_FONT, activebackground="#D6EFDC", activeforeground="black", borderwidth=5, relief="raised",
                        command=lambda: open_modal(HelpDialog))
    btn_wzd.grid(row=0, column=0, sticky="nsew")

    btn_hlp = tk.Button(wzd_hlp_frame, font=LBL_FONT, activebackground="#D6EFDC", activeforeground="black", borderwidth=5, relief="raised",
                        command=lambda: open_modal(HelpTwisterDialog))
    btn_hlp.grid(row=1, column=0, sticky="nsew")

    # --- Direction re 1 ---
    btn_ri = tk.Button(panel1, text="↻", font=BIG_BIG_FONT, borderwidth=5, relief="raised", command=lambda: setattr(state, "direction", True))
    btn_ri.grid(row=3, column=1, sticky="e")

    # --- twist mode 2 ---
    btn_twist = tk.Button(panel1, font=BIG_FONT, borderwidth=5, relief="raised", command=toggle_twist)
    btn_twist.grid(row=3, column=2, columnspan=2, sticky="nsew", padx=PAD_X, pady=PAD_Y)

     # --- service + calibration + statistic (same "position": row=3, col=6, split vertically) ---
    tmp_frame = tk.Frame(panel1, bg="black")
    tmp_frame.grid(row=3, column=4, columnspan=2, sticky="nsew", padx=PAD_X, pady=PAD_Y)

    tmp_frame.rowconfigure(0, weight=1)
    tmp_frame.columnconfigure(0, weight=2)        
    tmp_frame.columnconfigure(1, weight=1)

    # --- Direction li 3
    btn_le = tk.Button(tmp_frame, text="↺", font=BIG_BIG_FONT, borderwidth=5, relief="raised", command=lambda: setattr(state, "direction", False))
    btn_le.grid(row=0, column=0, sticky="w")

    # --- CPU Temp
    temperatur = tk.Label(tmp_frame, text=f"CPU:\n{state.cpu_temp} °C", fg="white", bg="black", font=("Arial", 10, "normal"))
    temperatur.grid(row=0, column=1, sticky="e",padx=PAD_X)

    # --- service + calibration + statistic (same "position": row=3, col=6, split vertically) ---
    svc_cal_frame = tk.Frame(panel1, bg=panel1.cget("bg"))
    svc_cal_frame.grid(row=3, column=6, sticky="nsew", padx=PAD_X, pady=PAD_Y)

    svc_cal_frame.rowconfigure(0, weight=1)
    svc_cal_frame.rowconfigure(1, weight=1)        
    svc_cal_frame.columnconfigure(0, weight=1)

    btn_service = tk.Button(svc_cal_frame, font=SVC_FONT, borderwidth=5, relief="raised", command=lambda: open_modal(LoginPopup))
    btn_service.grid(row=0, column=0, sticky="nsew")

    btn_config = tk.Button(svc_cal_frame, font=SVC_FONT, borderwidth=5, relief="raised")
    btn_config.grid(row=1, column=0, sticky="nsew")
    
    # ================= UPDATE LOOP =================
    # ------ loop to update  windows variables ------
    def update():
        nonlocal _update_job, temperatur
        global cpu_temp_counter
        
        cpu_temp_counter += 1
        if cpu_temp_counter >= 100:  # 10 seconds at 100ms
            cpu_temp()
            cpu_temp_counter = 0
            temperatur.config(text=f"CPU:\n{state.cpu_temp} °C")
            if isinstance(state.cpu_temp, (int, float)) and state.cpu_temp > ALERT_CPU_TEMP:
                temperatur.config(fg="red", font=("Arial", 10, "bold"))
            else:
                temperatur.config(fg="white", font=("Arial", 10, "normal"))
        t = language.texts[state.language]
        is_safe = state.machine_state == SAFE
        is_running = state.machine_state == RUNNING
        is_idle = state.machine_state == IDLE
        lbl_rpm.config(text=f"{state.target_rpm}")
        val_rpm.config(text=f"{int(state.actual_rpm)}\n{t['rpm']}")
        if state.remaining_turns == 0:
            lbl_cnt.config(text="∞", bg="DarkOliveGreen1", font=BIG_BIG_FONT)
            btn_plus_cnt.config(bg="DarkOliveGreen1", activebackground="DarkOliveGreen1")
            btn_minus_cnt.config(bg="DarkOliveGreen1", activebackground="DarkOliveGreen1")
            btn_plus_cnt.config(state=DISABLED if is_running else NORMAL)
            btn_minus_cnt.config(state=DISABLED if is_running else NORMAL)
        else:
            lbl_cnt.config(
                text=f"{int(state.remaining_turns)}\n{t['counter']}",
                bg="khaki1",
                font=BIG_FONT
            )
            btn_plus_cnt.config(bg="khaki1", activebackground="khaki1")
            btn_minus_cnt.config(bg="khaki1", activebackground="khaki1")
        val_cnt.config(text=f"{int(state.completed_turns)}")
        lbl_state.config(
            text=f"{t['state']}:\n"
                f"{state.machine_state}"
                f"{' ' + (t['cw'] if state.direction else t['ccw']) if state.machine_state == RUNNING else ''}\n"
                f"({state.user_role})",
            bg="green" if is_running else "red" if is_safe else "medium purple"
        )
        lock_lbl.config(text=t["locked"] if state.motor_locked else t["unlocked"],
                        bg="dark orange" if state.motor_locked else "burlywood")
        btn_start.config(text=t["start"])
        btn_center.config(text=t["center"])
        btn_stop.config(text=t["stop"])
        btn_lang.config(text=f"{t['language']}\n{state.language}")
        btn_lcfg.config(text=f"Load {t['config']}")
        btn_scfg.config(text=f"Save {t['config']}")
        hint.config(text=f"{t['loaded_recipe']}:\n" f"{state.current_profile}", font=LBL_FONT)
        lbl_lcfg.config(text=f"\u2139 {state.current_profile}", font=LBL_FONT, anchor="w")
        btn_wzd.config(text=t["wizard"], bg="#afafaf")
        btn_hlp.config(text= f"\u2139 {t['help']}", bg="#afafaf")
        btn_service.config(text=t["service"], bg="yellow" if state.user_role == SERVICE or state.user_role == CALIBRATION or state.user_role == STATISTIC else "grey")
        if state.user_role == CALIBRATION:
            btn_config.config(text=t["calibration"], bg="yellow" if state.user_role == CALIBRATION else "grey", command=toggle_calibration)
        elif state.user_role == STATISTIC:
            btn_config.config(text=t["statistic"], bg="yellow" if state.user_role == STATISTIC else "grey", command=lambda: open_modal(StatisticDialog))
        else:
            btn_config.config(text=t["configuration"], bg="yellow" if state.user_role == SERVICE else "grey", command=lambda: open_modal(ConfigEditor))
            
        btn_ri.config(bg="green" if state.direction else "gray", activebackground="lightgreen")
        btn_le.config(bg="green" if state.direction == False else "gray", activebackground="lightgreen")
        btn_twist.config(text=t["twist"] if state.twist_mode else t["serve"],
                         bg="lightblue" if state.twist_mode else "orange",
                         activebackground="aqua" if state.twist_mode else "gold")

        # --- block buttons for use ---
        btn_stop.config(state=NORMAL if not is_idle else DISABLED)
        btn_start.config(state=NORMAL if is_idle else DISABLED)
        btn_center.config(state=NORMAL if is_idle else DISABLED)
        btn_lang.config(state=NORMAL if is_idle else DISABLED)
        btn_lcfg.config(state=NORMAL if is_idle else DISABLED)
        btn_scfg.config(state=NORMAL if is_idle else DISABLED)
        btn_service.config(state=NORMAL if is_idle or is_safe else DISABLED)
        btn_config.config(state=NORMAL if is_idle or is_safe else DISABLED)
        btn_ri.config(state=NORMAL if is_idle else DISABLED)
        btn_le.config(state=NORMAL if is_idle else DISABLED)
        btn_twist.config(state=NORMAL if is_idle else DISABLED)
        btn_hlp.config(state=NORMAL if is_idle else DISABLED)
        btn_wzd.config(state=NORMAL if is_idle else DISABLED)
        
        throttle_active = state.throttle_percent > THROTTLE_START
        if not throttle_active:
            percent = int(state.actual_rpm / state.target_rpm * 100) if state.target_rpm > 0 else 0
        else:
            percent = int(state.throttle_percent * 100)
        #percent = int(state.throttle_percent * 100)

        throttle_bar["value"] = percent

        # color change, depend of throttle percent
        color = gradient_color(percent)
        bg_color = style.lookup("Custom.Horizontal.TProgressbar", "background")
        percent_label.config(text=f"{percent} %", fg=color , bg=bg_color if percent > 75 else "black")
        
        if root.winfo_exists():
            _update_job = root.after(UPDATE_MS, update)
        else:
            _update_job = None
        
    update()

    root.mainloop()
