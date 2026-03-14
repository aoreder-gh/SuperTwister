# ================================================================================================
# Super Twister 3001
# config_editor.py --- Dialog to edit configuration settings
# @author    Andreas Reder <aoreder@googlemail.com>
# ================================================================================================


import os
import shutil
import datetime
import hashlib
import tkinter as tk
from tkinter import ttk

import state
from ui.base_dialog import BaseDialog
from configs.config import SERVICE, OPERATOR
from configs.validation import VALIDATION_SERVICE, VALIDATION_OPERATOR
from configs.parameter_help import HELP_TEXTS
from configs import language
from utils.debug import dprint


CONFIG_PATH = os.path.join("configs", "config.py")
BACKUP_DIR = "configs"
FACTORY_CONFIG_PATH = os.path.join("configs", "config_factory.py")
MAX_BACKUPS = 3

# ==============================================================
#  Industrial Color Scheme
# ==============================================================

BG_MAIN = "#dcdcdc"
BG_PANEL = "#cfcfcf"
BG_ROW = "#e5e5e5"

BG_ROW_ALT = "#dddddd"   # optional alternating rows

COLOR_BUTTON = "#d0d0d0"
COLOR_BUTTON_ACTIVE = "#c0c0c0"

COLOR_HEADER = "#4a4a4a"
COLOR_HEADER_TEXT = "white"

# ==============================================================
# Parameter Groups
# ==============================================================

PARAMETER_GROUPS = {

    "System": [
        "DEBUG",
        "FULLSCREEN",
        "width",
        "height",
        "UPDATE_MS"
    ],

    "Stepper": [
        "DIR_RIGHT",
        "DIR_LEFT",
        "TWIST_MODE",
        "MICROSTEPS",
        "PWM_DUTY",
        "ENCODER_TIME",
        "SLEEP_TIME",
        "CENTER_RPM",
        "CENTER_OFFSET_STEPS"
    ],

    "Ramp / Motion": [
        "ACCEL_FAST",
        "ACCEL_SLOW",
        "DECEL_FAST",
        "DECEL_SLOW",
        "RESONANCE_MIN",
        "RESONANCE_MAX",
        "RAMP_TIME",
        "STOP_RAMP_TIME",
        "STOP_HARD_RPM_THRESHOLD",
        "PWM_UPDATE_THRESHOLD"
    ],

    "Throttle": [
        "THROTTLE_START",
        "MAX_RPM",
        "MIN_RPM",
        "STEP_RPM",
        "FAST_STEP",
        "MAX_TWIST",
        "START_RPM"
    ],

    "Profile": [
        "DEFAULT_PROFILE"
    ]
}

# ==============================================================
#  Touch Selection Dialog
# ==============================================================

class TouchSelectionDialog(tk.Toplevel):

    def __init__(self, parent, title, values, callback):
        super().__init__(parent)

        self.parent = parent
        self.callback = callback
        self.update_idletasks()
        x = self.winfo_x()
        self.geometry(f"+{x}+0")
        
        # ------------------------------------------------------
        # Window Setup
        # ------------------------------------------------------
        max_height = 560
        width = 500

        self.geometry(f"{width}x{max_height}")
        self.resizable(False, False)
        self.configure(bg=BG_MAIN)

        self.transient(parent)
        self.grab_set()
        self.focus_force()

        # ------------------------------------------------------
        # Layout
        # ------------------------------------------------------
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # ---------------- HEADER ----------------
        header = tk.Frame(self, bg=COLOR_HEADER, height=60)
        header.grid(row=0, column=0, sticky="ew")
        header.grid_propagate(False)

        tk.Label(
            header,
            text=title,
            font=("Arial", 20, "bold"),
            bg=COLOR_HEADER,
            fg="white"
        ).pack(expand=True)

        # ---------------- SCROLL AREA ----------------
        scroll_frame = tk.Frame(self, bg=BG_PANEL)
        scroll_frame.grid(row=1, column=0, sticky="nsew")

        canvas = tk.Canvas(
            scroll_frame,
            bg=BG_PANEL,
            highlightthickness=0
        )
        canvas.pack(side="left", fill="both", expand=True)

        style = ttk.Style()
        style.configure("Dialog.Vertical.TScrollbar", width=30)

        scrollbar = ttk.Scrollbar(
            scroll_frame,
            orient="vertical",
            command=canvas.yview,
            style="Dialog.Vertical.TScrollbar"
        )
        scrollbar.pack(side="right", fill="y")

        canvas.configure(yscrollcommand=scrollbar.set)

        self.button_container = tk.Frame(canvas, bg=BG_PANEL)

        self.canvas_window = canvas.create_window(
            (0, 0),
            window=self.button_container,
            anchor="nw"
        )

        def resize(event):
            canvas.itemconfig(self.canvas_window, width=event.width)

        canvas.bind("<Configure>", resize)

        self.button_container.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all"))
        )

        # Finger scroll support
        canvas.bind("<ButtonPress-1>", self._start_scroll)
        canvas.bind("<B1-Motion>", self._scroll_move)

        self.canvas = canvas

        # ---------------- Buttons ----------------
        for val in values:
            tk.Button(
                self.button_container,
                text=str(val),
                font=("Arial", 18),
                height=2,
                bg=COLOR_BUTTON,
                activebackground=COLOR_BUTTON_ACTIVE,
                relief="raised",
                bd=3,
                command=lambda v=val: self._select(v)
            ).pack(fill="x", padx=40, pady=6)

        # ---------------- FOOTER ----------------
        footer = tk.Frame(self, bg=BG_PANEL, height=70)
        footer.grid(row=2, column=0, sticky="ew")
        footer.grid_propagate(False)

        tk.Button(
            footer,
            text="CLOSE",
            font=("Arial", 16, "bold"),
            bg="#b94a48",
            activebackground="#953b39",
            fg="white",
            relief="raised",
            bd=3,
            height=2,
            command=self._close
        ).pack(fill="x", padx=40, pady=12)

        self.protocol("WM_DELETE_WINDOW", self._close)

    # ----------------------------------------------------------
    # Scroll Support
    # ----------------------------------------------------------

    def _start_scroll(self, event):
        self.canvas.scan_mark(event.x, event.y)

    def _scroll_move(self, event):
        self.canvas.scan_dragto(event.x, event.y, gain=1)

    # ----------------------------------------------------------
    # Selection
    # ----------------------------------------------------------

    def _select(self, value):
        self.callback(value)
        self._close()

    def _close(self):
        try:
            self.grab_release()
        except:
            pass
        self.destroy()

# ==============================================================
#  Modern Slider Widget
# ==============================================================

class ModernSliderWidget(tk.Frame):

    def __init__(self, parent, name, value,
                 min_val, max_val,
                 callback):

        super().__init__(parent, bd=1, relief="groove", bg=BG_ROW)

        self.name = name
        self.callback = callback
        self.min_val = min_val
        self.max_val = max_val
        self.range = max_val - min_val

        # Detect float range
        if isinstance(min_val, float) or isinstance(max_val, float):

            # determine decimal precision
            if self.range <= 1:
                self.resolution = 0.001
                self.fine_step = 0.001
            elif self.range <= 10:
                self.resolution = 0.01
                self.fine_step = 0.01
            else:
                self.resolution = 0.1
                self.fine_step = 0.01

        else:
            # integer range
            if self.range <= 100:
                self.resolution = 1
                self.fine_step = 1
            elif self.range <= 1000:
                self.resolution = 5
                self.fine_step = 1
            else:
                self.resolution = 10
                self.fine_step = 5

        self.var = tk.DoubleVar(value=value)

        tk.Button(self,
                  text="−",
                  font=("Arial", 16),
                  width=3,
                  bg=COLOR_BUTTON,
                  activebackground=COLOR_BUTTON_ACTIVE,
                  relief="raised",
                  bd=3,
                  command=self._fine_minus).pack(side="left")

        self.scale = tk.Scale(
            self,
            from_=min_val,
            to=max_val,
            orient="horizontal",
            resolution=self.resolution,
            showvalue=False,
            length=260,
            sliderlength=30,
            width=20,
            variable=self.var,
            bd=0,
            highlightthickness=0,
            troughcolor="#c8c8c8",
            bg=BG_ROW,
            command=self._on_change
        )

        self.scale.pack(side="left")

        tk.Button(self,
                  text="+",
                  font=("Arial", 16),
                  width=3,
                  command=self._fine_plus).pack(side="left")

        self.value_label = tk.Label(self,
                                    text=str(value),
                                    font=("Arial", 14, "bold"),
                                    width=6)
        self.value_label.pack(side="left", padx=6)

    def _on_change(self, event=None):
        value = self.var.get()

        if isinstance(self.min_val, float) or isinstance(self.max_val, float):
            value = round(value, 3)
        else:
            value = int(value)

        self.value_label.config(text=str(value))
        self.callback(self.name, value)

    def _fine_minus(self):
        self.var.set(self.var.get() - self.fine_step)
        self._on_change()

    def _fine_plus(self):
        self.var.set(self.var.get() + self.fine_step)
        self._on_change()


# ==============================================================
#  Config Editor
# ==============================================================

class ConfigEditor(BaseDialog):

    def __init__(self, root):
        super().__init__(root,
                         title="Configuration",
                         width=1020,
                         height=560)

        self.t = language.texts[state.language]

        self.original_values = {}
        self.current_values = {}
        self.widgets = {}
        self.labels = {}

        self.original_hash = self._file_hash(CONFIG_PATH)

        self._create_backup()
        self._load_config()
        self._build_ui()

    # ==============================================================
    #  define group header
    # ==============================================================

    def _add_group_header(self, title):

        header = tk.Frame(
            self.table,
            bg="#b8b8b8",
            height=30,
            bd=1,
            relief="ridge"
        )
        header.grid(row=self.row, column=0,
                    sticky="ew", padx=6, pady=(12, 4))
        header.grid_propagate(False)

        tk.Label(
            header,
            text=title,
            font=("Arial", 14, "bold"),
            bg="#b8b8b8",
            anchor="w"
        ).pack(fill="both", padx=10)

        self.row += 1

    # ----------------------------------------------------------
    # Utility
    # ----------------------------------------------------------

    def _file_hash(self, path):
        with open(path, "rb") as f:
            return hashlib.md5(f.read()).hexdigest()

    # ----------------------------------------------------------
    # Backup
    # ----------------------------------------------------------

    def _create_backup(self):

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        backup_name = f"config_backup_{timestamp}.py"
        backup_path = os.path.join(BACKUP_DIR, backup_name)

        shutil.copy(CONFIG_PATH, backup_path)

        # Keep only last MAX_BACKUPS
        backups = sorted(
            [f for f in os.listdir(BACKUP_DIR)
            if f.startswith("config_backup_")],
            reverse=True
        )

        for old_backup in backups[MAX_BACKUPS:]:
            os.remove(os.path.join(BACKUP_DIR, old_backup))

    # ----------------------------------------------------------
    # Load Config
    # ----------------------------------------------------------

    def _load_config(self):

        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            lines = f.readlines()

        section = None

        for line in lines:
            stripped = line.strip()

            if stripped.startswith("# changeable by SERVICE"):
                section = SERVICE
                continue

            if stripped.startswith("# changeable by OPERATOR"):
                section = OPERATOR
                continue

            if "=" in stripped and not stripped.startswith("#") and section:
                name, value = stripped.split("=", 1)
                name = name.strip()
                value = value.split("#")[0].strip()
                parsed = eval(value)

                self.original_values[name] = {
                    "value": parsed,
                    "section": section
                }

        self.current_values = {
            k: v["value"] for k, v in self.original_values.items()
        }

    def _open_backup_manager(self):

        top = tk.Toplevel(self)
        top.geometry("600x300")
        top.title("Backup Manager")
        top.configure(bg="#dcdcdc")
        top.transient(self)
        top.grab_set()

        tk.Label(
            top,
            text="Available Backups",
            font=("Arial", 18, "bold"),
            bg="#4a4a4a",
            fg="white"
        ).pack(fill="x")

        list_frame = tk.Frame(top, bg="#dcdcdc")
        list_frame.pack(fill="both", expand=True, pady=10)

        canvas = tk.Canvas(list_frame, bg="#dcdcdc", highlightthickness=0)
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical",
                                command=canvas.yview)

        canvas.configure(yscrollcommand=scrollbar.set)

        scroll_content = tk.Frame(canvas, bg="#dcdcdc")
        canvas.create_window((0, 0), window=scroll_content, anchor="nw")

        scroll_content.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        backups = sorted(
            [f for f in os.listdir(BACKUP_DIR)
            if f.startswith("config_backup_")],
            reverse=True
        )

        for idx, file in enumerate(backups):

            row = tk.Frame(scroll_content, bg="#e5e5e5", bd=1, relief="groove")
            row.pack(fill="x", padx=10, pady=5)

            pretty_date = file.replace("config_backup_", "").replace(".py", "")
            pretty_date = pretty_date.replace("_", " ")

            tk.Label(
                row,
                text=pretty_date,
                font=("Arial", 14),
                bg="#e5e5e5"
            ).pack(side="left", padx=15)

            tk.Button(
                row,
                text="RESTORE",
                font=("Arial", 12, "bold"),
                bg="#d9534f",
                fg="white",
                relief="raised",
                command=lambda f=file: self._restore_backup(f, top)
            ).pack(side="right", padx=10)

        tk.Button(
            list_frame,
            text="CLOSE",
            font=("Arial", 16, "bold"),
            bg="#b94a48",
            activebackground="#953b39",
            fg="white",
            relief="raised",
            bd=4,
            height=2,
            command=top.destroy
        ).pack(fill="x", padx=40, pady=15)

    # ----------------------------------------------------------
    # restore backup
    # ----------------------------------------------------------

    def _restore_backup(self, filename, dialog):
        confirm = tk.Toplevel(self)
        confirm.geometry("500x250")
        confirm.title("Confirm Restore")
        confirm.configure(bg="#dcdcdc")
        confirm.transient(self)
        confirm.grab_set()

        # Header
        tk.Label(
            confirm,
            text="Restore Backup?",
            font=("Arial", 18, "bold"),
            bg="#4a4a4a",
            fg="white"
        ).pack(fill="x")

        # Content
        pretty_date = filename.replace("config_backup_", "").replace(".py", "")
        pretty_date = pretty_date.replace("_", " ")

        message = (
            f"Restore backup from:\n\n"
            f"{pretty_date}\n\n"
            "Current configuration will be overwritten."
        )

        tk.Label(
            confirm,
            text=message,
            font=("Arial", 14),
            bg="#dcdcdc",
            justify="center"
        ).pack(expand=True)

        # Button area
        btn_frame = tk.Frame(confirm, bg="#dcdcdc")
        btn_frame.pack(pady=20)

        # Cancel button
        tk.Button(
            btn_frame,
            text="CANCEL",
            font=("Arial", 14, "bold"),
            width=12,
            bg="#b0b0b0",
            relief="raised",
            bd=3,
            command=confirm.destroy
        ).pack(side="left", padx=15)

        # Restore button
        tk.Button(
            btn_frame,
            text="RESTORE",
            font=("Arial", 14, "bold"),
            width=12,
            bg="#b94a48",
            fg="white",
            activebackground="#953b39",
            relief="raised",
            bd=3,
            command=lambda: self._execute_restore(filename, confirm, dialog)
        ).pack(side="left", padx=15)

    # ----------------------------------------------------------
    # execute restore backup
    # ----------------------------------------------------------

    def _execute_restore(self, filename, confirm_dialog, backup_dialog):

        backup_path = os.path.join(BACKUP_DIR, filename)

        shutil.copy(backup_path, CONFIG_PATH)

        confirm_dialog.destroy()
        backup_dialog.destroy()

        self.info_bar.config(
            text="Backup restored. Restart required.",
            bg="#ccffcc"
        )    

    # ----------------------------------------------------------
    # UI
    # ----------------------------------------------------------

    def _build_ui(self):

        style = ttk.Style()
        style.theme_use("default")

        style.configure(
            "Vertical.TScrollbar",
            gripcount=0,
            background="#bfbfbf",
            darkcolor="#a8a8a8",
            lightcolor="#d9d9d9",
            troughcolor="#cfcfcf",
            bordercolor="#7a7a7a",
            arrowcolor="black",
            width=30
        )

        style.layout("Vertical.TScrollbar", [
            ('Vertical.Scrollbar.trough',
                {'children': [
                    ('Vertical.Scrollbar.thumb', {'expand': '1', 'sticky': 'nswe'})
                ],
                'sticky': 'ns'})
        ])

        # ==========================================================
        # HEADER
        # ==========================================================
        header = tk.Frame(
            self.content,
            bg=COLOR_HEADER,
            height=30,
            bd=2,
            relief="ridge"
        )
        header.pack(fill="x", padx=15, pady=(0, 5))
        header.pack_propagate(False)
        role_text = "Configuration [SERVICE MODE]*" if state.user_role == SERVICE else "Configuration [OPERATOR MODE]*"
        tk.Label(
            header,
            text=role_text,
            bg=COLOR_HEADER,
            fg=COLOR_HEADER_TEXT,
            font=("Arial", 18, "bold")
        ).pack(expand=True)

        # ==========================================================
        # SCROLL PANEL
        # ==========================================================
        scroll_panel = tk.Frame(
            self.content,
            bg=BG_PANEL,
            bd=2,
            relief="ridge"
        )
        scroll_panel.pack(fill="both", expand=True, padx=15, pady=5)

        canvas = tk.Canvas(
            scroll_panel,
            bg=BG_PANEL,
            highlightthickness=0
        )
        canvas.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(
            scroll_panel,
            orient="vertical",
            command=canvas.yview
        )
        scrollbar.pack(side="right", fill="y")

        canvas.configure(yscrollcommand=scrollbar.set)

        self.table = tk.Frame(canvas, bg=BG_PANEL)

        self.canvas_window = canvas.create_window(
            (0, 0),
            window=self.table,
            anchor="nw"
        )

        def resize_table(event):
            canvas.itemconfig(self.canvas_window, width=event.width)

        canvas.bind("<Configure>", resize_table)

        self.table.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all"))
        )

        # Build parameter rows
        self.row = 0

        dprint("Original values:" + str(self.original_values))

        self.row = 0

        for group_name, param_list in PARAMETER_GROUPS.items():

            visible_params = []

            for name in param_list:

                if name == "DIR_LEFT":
                    continue

                if name not in self.original_values:
                    continue

                section = self.original_values[name]["section"]

                # Role filtering
                if state.user_role == OPERATOR and section == SERVICE:
                    continue

                visible_params.append(name)

            if visible_params:
                self._add_group_header(group_name)

                for name in visible_params:
                    self._add_parameter_row(name)

        # ==========================================================
        # INFO BAR
        # ==========================================================
        self.info_bar = tk.Label(
            self.content,
            text="",
            font=("Arial", 14),
            anchor="w",
            relief="sunken",
            bg="#d8d8d8",
            fg="#202020",
            bd=1,
            height=2
        )
        self.info_bar.pack(fill="x", padx=15, pady=(0, 5))

        # ==========================================================
        # SAVE PANEL
        # ==========================================================
        save_panel = tk.Frame(
            self.content,
            bg=BG_PANEL,
            height=30,
            bd=2,
            relief="ridge"
        )

        save_panel.pack(fill="x", padx=15, pady=(0, 5))
        save_panel.pack_propagate(False)

        # 3 columns
        save_panel.grid_columnconfigure(0, weight=1)
        save_panel.grid_columnconfigure(1, weight=1)
        save_panel.grid_columnconfigure(2, weight=1)

        # ---------------- BACKUPS (left) ----------------
        tk.Button(
            save_panel,
            text="BACKUPS",
            font=("Arial", 14, "bold"),
            bg=COLOR_BUTTON,
            activebackground=COLOR_BUTTON_ACTIVE,
            relief="raised",
            bd=3,
            width=16,
            command=self._open_backup_manager
        ).grid(row=0, column=0, pady=18)

        # ---------------- SAVE (center) ----------------
        tk.Button(
            save_panel,
            text="SAVE",
            font=("Arial", 18, "bold"),
            bg="#4a7a4a",
            fg="white",
            activebackground="#3f6b3f",
            relief="raised",
            bd=4,
            width=16,
            command=self._save
        ).grid(row=0, column=1, pady=18)

        # ---------------- FACTORY RESET (right) ----------------
        tk.Button(
            save_panel,
            text="FACTORY RESET",
            font=("Arial", 14, "bold"),
            bg="#b94a48",
            fg="white",
            activebackground="#953b39",
            relief="raised",
            bd=3,
            width=16,
            command=self._confirm_factory_reset
        ).grid(row=0, column=2, pady=18)

    # ----------------------------------------------------------
    # confirm factory reset
    # ----------------------------------------------------------

    def _confirm_factory_reset(self):

        confirm = tk.Toplevel(self)
        confirm.geometry("520x260")
        confirm.title("Factory Reset")
        confirm.configure(bg="#dcdcdc")
        confirm.transient(self)
        confirm.grab_set()

        tk.Label(
            confirm,
            text="Factory Reset",
            font=("Arial", 18, "bold"),
            bg="#4a4a4a",
            fg="white"
        ).pack(fill="x")

        message = (
            "All settings will be reset\n"
            "to factory defaults.\n\n"
            "Current configuration will be lost."
        )

        tk.Label(
            confirm,
            text=message,
            font=("Arial", 14),
            bg="#dcdcdc",
            justify="center"
        ).pack(expand=True)

        btn_frame = tk.Frame(confirm, bg="#dcdcdc")
        btn_frame.pack(pady=20)

        tk.Button(
            btn_frame,
            text="CANCEL",
            font=("Arial", 14, "bold"),
            width=12,
            bg="#b0b0b0",
            relief="raised",
            bd=3,
            command=confirm.destroy
        ).pack(side="left", padx=15)

        tk.Button(
            btn_frame,
            text="RESET",
            font=("Arial", 14, "bold"),
            width=12,
            bg="#b94a48",
            fg="white",
            activebackground="#953b39",
            relief="raised",
            bd=3,
            command=lambda: self._execute_factory_reset(confirm)
        ).pack(side="left", padx=15)

    # ----------------------------------------------------------
    # execute factory reset
    # ----------------------------------------------------------

    def _execute_factory_reset(self, confirm_dialog):

        if not os.path.exists(FACTORY_CONFIG_PATH):
            self.info_bar.config(
                text="Factory config not found.",
                bg="#ffcccc"
            )
            confirm_dialog.destroy()
            return

        shutil.copy(FACTORY_CONFIG_PATH, CONFIG_PATH)

        confirm_dialog.destroy()

        self.info_bar.config(
            text="Factory settings restored. Restart required.",
            bg="#ccffcc"
        )    
        
    # ----------------------------------------------------------
    # Parameter Row
    # ----------------------------------------------------------

    def _add_parameter_row(self, name):

        value = self.current_values[name]
        validation = self._get_validation(name)

        section = self.original_values[name]["section"]

        if section == SERVICE:
            base_bg = "#eed08b"
        else:
            base_bg = "#6498f0"

        base_bg = BG_ROW if self.row % 2 == 0 else BG_ROW_ALT

        row_frame = tk.Frame(
            self.table,
            bg=base_bg,
            height=54,
            bd=1,
            relief="groove"
        )

        # store reference for validation highlighting
        self.widgets[name] = {
            "frame": row_frame,
            "base_bg": base_bg
        }

        row_frame.grid(row=self.row, column=0,
                    sticky="ew", padx=8, pady=4)

        row_frame.grid_columnconfigure(2, weight=1)

        # Label
        tk.Label(
            row_frame,
            text=name,
            font=("Arial", 14),
            bg=row_frame["bg"],
            anchor="w",
            width=18
        ).grid(row=0, column=0, padx=12, sticky="w")

        # Info
        tk.Button(
            row_frame,
            text="INFO",
            font=("Arial", 10),
            bg=COLOR_BUTTON,
            activebackground=COLOR_BUTTON_ACTIVE,
            relief="raised",
            bd=2,
            width=6,
            command=lambda n=name:
            self._open_help_window(n)
        ).grid(row=0, column=1, padx=8)

        widget = self._create_widget(row_frame, name, value, validation)
        widget.grid(row=0, column=2, padx=10, sticky="w")

        self.row += 1

    # ----------------------------------------------------------
    # Widget Factory (FULLY RESTORED)
    # ----------------------------------------------------------

    def _create_widget(self, parent, name, value, validation):

        if name == "DIR_RIGHT":
            return self._create_direction_widget(parent, value)

        if isinstance(value, bool):
            btn = tk.Button(
                parent,
                text=str(value),
                font=("Arial", 16),
                width=8,
                bg=COLOR_BUTTON,
                activebackground=COLOR_BUTTON_ACTIVE,
                relief="raised",
                bd=3,
                command=lambda:
                self._toggle_bool(name, btn)
            )
            return btn

        if validation and "allowed" in validation:
            btn = tk.Button(
                parent,
                text=str(value),
                font=("Arial", 16),
                width=12,
                bg=COLOR_BUTTON,
                activebackground=COLOR_BUTTON_ACTIVE,
                relief="raised",
                bd=3,
                command=lambda:
                TouchSelectionDialog(
                    self,
                    name,
                    validation["allowed"],
                    lambda v:
                    self._update_selection(name, btn, v)
                )
            )
            return btn

        if validation and "min" in validation:
            return ModernSliderWidget(
                parent,
                name,
                value,
                validation["min"],
                validation["max"],
                self._update_value
            )

        entry = tk.Entry(
            parent,
            font=("Arial", 14),
            width=15
        )
        entry.insert(0, str(value))
        entry.bind("<FocusOut>",
                lambda e:
                self._update_value(name, entry.get()))
        return entry
    
    # ----------------------------------------------------------
    # Direction Widget (DIR_RIGHT / DIR_LEFT)
    # ----------------------------------------------------------

    def _create_direction_widget(self, parent, value):

        frame = tk.Frame(parent, bg=parent["bg"])

        btn_right = tk.Button(
            frame,
            text="Right",
            font=("Arial", 16),
            width=8,
            command=lambda:
            self._set_direction(1, btn_right, btn_left)
        )

        btn_left = tk.Button(
            frame,
            text="Left",
            font=("Arial", 16),
            width=8,
            command=lambda:
            self._set_direction(0, btn_right, btn_left)
        )

        btn_right.pack(side="left", padx=5)
        btn_left.pack(side="left", padx=5)

        # initial highlight
        if value == 1:
            btn_right.config(bg="#9ecb8f")
        else:
            btn_left.config(bg="#9ecb8f")

        return frame


    def _set_direction(self, val, btn_right, btn_left):

        self.current_values["DIR_RIGHT"] = val
        self.current_values["DIR_LEFT"] = 0 if val == 1 else 1

        btn_right.config(bg="#9ecb8f" if val == 1 else "SystemButtonFace")
        btn_left.config(bg="#9ecb8f" if val == 0 else "SystemButtonFace")

        self._update_info_bar("DIR_RIGHT")
        
    # ----------------------------------------------------------
    # Validation / Help / Info
    # ----------------------------------------------------------

    def _get_validation(self, name):
        return (VALIDATION_SERVICE.get(name)
                or VALIDATION_OPERATOR.get(name))

    def _get_help_text(self, name):

        text = HELP_TEXTS.get(name, {}).get(
            state.language, "")

        validation = self._get_validation(name)

        if validation:
            if "allowed" in validation:
                text += "\n\nAllowed: " + ", ".join(
                    str(v) for v in validation["allowed"])
            elif "min" in validation:
                text += f"\n\nRange: {validation['min']} - {validation['max']}"

        return text

    def _update_info_bar(self, name, error=False):

        self.info_bar.config(
            text=self._get_help_text(name),
            bg="#ffcccc" if error else "#e6e6e6"
        )

    # ----------------------------------------------------------
    # Open Help Window (Auto Close + Fixed Close Button Area)
    # ----------------------------------------------------------

    def _open_help_window(self, name):

        top = tk.Toplevel(self)

        top.transient(self)
        top.lift()
        top.focus_force()
        top.attributes("-topmost", True)

        top.geometry("600x350")
        top.resizable(False, False)
        top.configure(bg="#f0f0f0")

        # Remove native window border for cleaner look (optional)
        # top.overrideredirect(True)

        # Grid layout
        top.grid_rowconfigure(1, weight=1)
        top.grid_columnconfigure(0, weight=1)

        # ==========================================================
        # HEADER
        # ==========================================================
        header = tk.Frame(top, bg=COLOR_HEADER, bd=3, relief="raised")
        header.grid(row=0, column=0, sticky="ew")

        tk.Label(
            header,
            text=name,
            bg="#3c3f41",
            fg="white",
            font=("Arial", 18, "bold")
        ).pack(pady=10)

        # ==========================================================
        # CONTENT AREA
        # ==========================================================
        content_frame = tk.Frame(top, bg="white")
        content_frame.grid(row=1, column=0, sticky="nsew")

        content_frame.grid_rowconfigure(0, weight=1)
        content_frame.grid_columnconfigure(0, weight=1)

        text_widget = tk.Text(
            content_frame,
            font=("Arial", 16),
            wrap="word",
            bg="white",
            bd=0,
            highlightthickness=0
        )

        text_widget.insert("1.0", self._get_help_text(name))
        text_widget.config(state="disabled")

        text_widget.grid(row=0, column=0,
                        sticky="nsew",
                        padx=20,
                        pady=20)

        # ==========================================================
        # FOOTER / CLOSE BUTTON
        # ==========================================================
        footer = tk.Frame(top, bg=BG_PANEL, bd=2, relief="groove")
        footer.grid(row=2, column=0, sticky="ew")

        tk.Button(
            footer,
            text="CLOSE",
            font=("Arial", 16, "bold"),
            bg="#b94a48",
            activebackground="#953b39",
            fg="white",
            relief="raised",
            bd=4,
            height=2,
            command=top.destroy
        ).pack(fill="x", padx=20, pady=15)

        # ==========================================================
        # AUTO CLOSE ON FOCUS LOSS
        # ==========================================================
        def on_focus_out(event):
            top.after(200, lambda: top.destroy())

        top.bind("<FocusOut>", on_focus_out)
        
    # ----------------------------------------------------------
    # Value Updates
    # ----------------------------------------------------------

    def _update_value(self, name, value):
        try:
            original_type = type(
                self.original_values[name]["value"])
            if original_type == int:
                value = int(float(value))
            elif original_type == float:
                value = float(value)
        except:
            return

        self.current_values[name] = value

    def _update_selection(self, name, button, value):
        self.current_values[name] = value
        button.config(text=str(value))

    def _toggle_bool(self, name, button):
        new_val = not self.current_values[name]
        self.current_values[name] = new_val
        button.config(text=str(new_val))

    # ----------------------------------------------------------
    # Save Configuration (REAL FILE WRITE)
    # ----------------------------------------------------------

    def _save(self):

        # Cross validation first
        errors, error_fields = self._cross_validate()

        if errors:
            self._highlight_errors(error_fields)
            self.info_bar.config(
                text="\n".join(errors),
                bg="#ffdddd"
            )
            return

        # Read original file
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            lines = f.readlines()

        if "DIR_RIGHT" in self.current_values:
            self.current_values["DIR_LEFT"] = (
                0 if self.current_values["DIR_RIGHT"] == 1 else 1
            )
        
        new_lines = []

        for line in lines:
            stripped = line.strip()
            
            if "=" in stripped and not stripped.startswith("#"):
                name = stripped.split("=")[0].strip()

                if name in self.current_values:
                    value = self.current_values[name]
                    line = f"{name} = {repr(value)}\n"

            new_lines.append(line)

        # Write to temporary file
        temp_path = CONFIG_PATH + ".tmp"

        with open(temp_path, "w", encoding="utf-8") as f:
            f.writelines(new_lines)

        # Compare hash
        new_hash = self._file_hash(temp_path)

        if new_hash == self.original_hash:
            os.remove(temp_path)
            self.info_bar.config(
                text="No changes detected.",
                bg="#e6e6e6"
            )
            return

        # Replace original file
        shutil.move(temp_path, CONFIG_PATH)

        self.info_bar.config(
            text="Configuration saved. Restart required.",
            bg="#ccffcc"
        )

        # reset errors
        self._highlight_errors([])

    def _cross_validate(self):

        cv = self.current_values
        errors = []
        error_fields = []

        if cv.get("MIN_RPM") >= cv.get("MAX_RPM"):
            errors.append("MIN_RPM must be < MAX_RPM")
            error_fields += ["MIN_RPM", "MAX_RPM"]

        if cv.get("ACCEL_SLOW") > cv.get("ACCEL_FAST"):
            errors.append("ACCEL_SLOW must be ≤ ACCEL_FAST")
            error_fields += ["ACCEL_SLOW", "ACCEL_FAST"]

        # DIR safety (optional but good)
        if cv.get("DIR_RIGHT") == cv.get("DIR_LEFT"):
            errors.append("DIR_RIGHT and DIR_LEFT must be opposite")
            error_fields += ["DIR_RIGHT"]

        return errors, error_fields

    def _highlight_errors(self, error_names):

        # reset all rows first
        for name, data in self.widgets.items():
            data["frame"].config(bg=data["base_bg"])

        # highlight errors
        for name in error_names:
            if name in self.widgets:
                self.widgets[name]["frame"].config(bg="#ffb3b3")
