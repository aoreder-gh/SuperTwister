#  /**
#   * Super Twister 3001
#   *
#   * @author    Andreas Reder <aoreder@gmail.com>
#   *
#   * @copyright Andreas Reder
#   * @version   1.0.0
#   */

import tkinter as tk

import state
from configs.config import SERVICE, IDLE
from hardware.throttle_adc import chan
from logic.config_io import save_config
from ui.base_dialog import BaseDialog


class StatisticDialog(BaseDialog):

    def __init__(self, root):
        super().__init__(root, title="Statistics", width=400, height=430)
        self.build_ui()
        self.update_voltage()
        state.machine_state = "SERVICE"

    def build_ui(self):

        self.lbl_voltage = tk.Label(
            self.content,
            font=("Arial", 18)
        )
        self.lbl_voltage.pack(pady=10)

        self.lbl_min = tk.Label(
            self.content,
            text=f"MIN: {state.throttle_min_v:.2f} V",
            font=("Arial", 14)
        )
        self.lbl_min.pack(pady=5)

        self.lbl_max = tk.Label(
            self.content,
            text=f"MAX: {state.throttle_max_v:.2f} V",
            font=("Arial", 14)
        )
        self.lbl_max.pack(pady=5)

        tk.Button(
            self.content,
            text="Learn MIN (release throttle)",
            font=("Arial", 14),
            height=2,
            command=self.learn_min
        ).pack(fill="x", padx=20, pady=5)

        tk.Button(
            self.content,
            text="Learn MAX (full throttle)",
            font=("Arial", 14),
            height=2,
            command=self.learn_max
        ).pack(fill="x", padx=20, pady=5)

        tk.Button(
            self.content,
            text="Save",
            font=("Arial", 16),
            height=2,
            bg="lightblue",
            command=self.save
        ).pack(fill="x", padx=20, pady=15)

    def learn_min(self):
        state.throttle_min_v = chan.voltage
        self.lbl_min.config(text=f"MIN: {state.throttle_min_v:.2f} V")

    def learn_max(self):
        state.throttle_max_v = chan.voltage - 0.05  # Subtract small offset to ensure we can reach 100%
        self.lbl_max.config(text=f"MAX: {state.throttle_max_v:.2f} V")

    def save(self):
        save_config()
        self.close()

    def update_voltage(self):
        try:
            self.lbl_voltage.config(text=f"Current: {chan.voltage:.2f} V")
        except:
            pass

        self.after(100, self.update_voltage)

    def close(self):
        state.machine_state = "IDLE"
        try:
            self.grab_release()
        except:
            pass
        self.destroy()
