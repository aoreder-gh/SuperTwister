# ==============================================================
# Super Twister 3001
# statistic_dialog
# dialog window to display statistics
# @author    Andreas Reder <aoreder@gmail.com>
# ==============================================================

import tkinter as tk

import state
from configs.config import SERVICE, IDLE
from hardware.throttle_adc import chan
from logic.config_io import save_config
from ui.base_dialog import BaseDialog


class StatisticDialog(BaseDialog):

    def __init__(self, root):
        super().__init__(root, title="Statistics", width=400, height=430)
        state.machine_state = SERVICE
        self.build_ui()

    def build_ui(self):
        self.lbl_runs = tk.Label(
            self.content,
            text=f"Total runs: {state.total_runs}",
            font=("Arial", 18)
        )
        self.lbl_runs.pack(pady=10)

        self.lbl_turns = tk.Label(
            self.content,
            text=f"Total turns: {state.total_turns}",
            font=("Arial", 14)
        )
        self.lbl_turns.pack(pady=10)

    def close(self):
        state.machine_state = IDLE
        self.destroy()
