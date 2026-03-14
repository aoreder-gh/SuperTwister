# ==============================================================
# Super Twister 3001
# Config Load/Save Functions
# @author    Andreas Reder <aoreder@googlemail.com>
# ==============================================================

import tkinter as tk
import state
from configs.config import SERVICE, OPERATOR
from ui.base_dialog import BaseDialog

SERVICE_CODE = "12345"
CALIBRATION_CODE = "12346"
STATISTIC_CODE = "12347"

class LoginPopup(BaseDialog):

    def __init__(self, root):
        super().__init__(root, title="Service Login", width=400, height=430)
        self.code = ""
        self.build_ui()

    # -------------------------------------------------
    # UI
    # -------------------------------------------------
    def build_ui(self):

        tk.Label(
            self.content,
            text="Enter Service Code",
            font=("Arial", 14)
        ).pack(pady=15)

        # Display field
        self.display = tk.Label(
            self.content,
            text="",
            font=("Arial", 18),
            bg="black",
            fg="white",
            height=1
        )
        self.display.pack(fill="x", padx=10, pady=10)

        self.msg = tk.Label(self.content, font=("Arial", 12))
        self.msg.pack(pady=5)

        # Keypad Frame
        keypad = tk.Frame(self.content)
        keypad.pack(expand=True)

        buttons = [
            "1", "2", "3",
            "4", "5", "6",
            "7", "8", "9",
            "<", "0", "Enter"
        ]

        for i, val in enumerate(buttons):

            btn = tk.Button(
                keypad,
                text=val,
                font=("Arial", 16),
                width=5,
                height=1,
                command=lambda v=val: self.key_press(v)
            )

            btn.grid(
                row=i // 3,
                column=i % 3,
                padx=5,
                pady=5,
                sticky="nsew"
            )

        for i in range(3):
            keypad.grid_columnconfigure(i, weight=1)

    # -------------------------------------------------
    # Key Handling
    # -------------------------------------------------
    def key_press(self, value):

        if value == "<":
            self.code = self.code[:-1]

        elif value == "Enter":
            self.validate_code()
            return

        else:
            if len(self.code) < 8:   # max length
                self.code += value

        self.update_display()

    # -------------------------------------------------
    def update_display(self):
        self.display.config(text="*" * len(self.code))

    # -------------------------------------------------
    def validate_code(self):
        if self.code == SERVICE_CODE:
            state.user_role = SERVICE
        elif self.code == CALIBRATION_CODE:
            state.user_role = "CALIBRATION"
        elif self.code == STATISTIC_CODE:
            state.user_role = "STATISTIC"
        else:
            state.user_role = OPERATOR

        self.close()

    # -------------------------------------------------
    def close(self):
        try:
            self.grab_release()
        except:
            pass
        self.destroy()

