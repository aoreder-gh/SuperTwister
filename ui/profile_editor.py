# ================================================================================================
# Super Twister 3001
# profile_editor.py --- Dialog to edit user profile settings
# @author    Andreas Reder <aoreder@googlemail.com>
# ================================================================================================

import tkinter as tk
import state
from logic.config_io import save_config
from ui.base_dialog import BaseDialog


class ProfileEditor(BaseDialog):

    def __init__(self, root):
        super().__init__(root, title="Profile Editor", width=400, height=430)
        self.build_ui()

    def build_ui(self):

        tk.Label(
            self.content,
            text="RPM",
            font=("Arial", 16)
        ).pack(pady=5)

        self.rpm = tk.IntVar(value=state.target_rpm)

        tk.Entry(
            self.content,
            textvariable=self.rpm,
            font=("Arial", 16),
            justify="center"
        ).pack(fill="x", padx=20, pady=5)

        tk.Label(
            self.content,
            text="Turns",
            font=("Arial", 16)
        ).pack(pady=5)

        self.turns = tk.IntVar(value=state.remaining_turns)

        tk.Entry(
            self.content,
            textvariable=self.turns,
            font=("Arial", 16),
            justify="center"
        ).pack(fill="x", padx=20, pady=5)

        self.twist = tk.BooleanVar(value=state.twist_mode)

        tk.Checkbutton(
            self.content,
            text="Twist mode",
            variable=self.twist,
            font=("Arial", 14)
        ).pack(pady=10)

        tk.Button(
            self.content,
            text="Save",
            font=("Arial", 16),
            height=2,
            bg="lightblue",
            command=self.save
        ).pack(fill="x", padx=20, pady=20)

    def save(self):
        state.target_rpm = self.rpm.get()
        state.remaining_turns = self.turns.get()
        state.twist_mode = self.twist.get()

        save_config()
        self.close()

    def close(self):
        try:
            self.grab_release()
        except:
            pass
        self.destroy()
