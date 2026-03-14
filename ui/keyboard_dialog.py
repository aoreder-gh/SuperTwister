# ================================================================================================
# Super Twister 3001
# keyboard_dialog.py --- On-screen keyboard dialog for text input
# @author    Andreas Reder <aoreder@googlemail.com>
# ================================================================================================

import tkinter as tk


class KeyboardDialog(tk.Toplevel):

    def __init__(self, root, initial_value=""):
        super().__init__(root)

        self.root = root
        self.result = None

        self.title("Keyboard")
        self.geometry("900x400")
        self.resizable(False, False)
        self.transient(root)

        # Zentrieren
        self.update_idletasks()
        x = root.winfo_rootx() + (root.winfo_width() // 2) - 450
        y = root.winfo_rooty() + (root.winfo_height() // 2) - 200
        self.geometry(f"+{x}+{y}")

        self.var = tk.StringVar(value=initial_value)

        self.build_ui()

    def build_ui(self):

        entry = tk.Entry(
            self,
            textvariable=self.var,
            font=("Arial", 22),
            justify="center"
        )
        entry.pack(fill="x", pady=10)

        keys_frame = tk.Frame(self)
        keys_frame.pack(expand=True)

        keys = (
            list("1234567890") +
            list("QWERTZUIOP") +
            list("ASDFGHJKL") +
            list("YXCVBNM-_")
        )

        cols = 10

        for i, k in enumerate(keys):
            btn = tk.Button(
                keys_frame,
                text=k,
                font=("Arial", 16),
                width=4,
                height=2,
                command=lambda c=k: self.add_char(c)
            )
            btn.grid(row=i // cols, column=i % cols, padx=3, pady=3)

        bottom = tk.Frame(self)
        bottom.pack(fill="x", pady=10)

        tk.Button(
            bottom,
            text="Backspace",
            font=("Arial", 16),
            height=2,
            command=self.backspace
        ).pack(side="left", expand=True, fill="x", padx=5)

        tk.Button(
            bottom,
            text="OK",
            font=("Arial", 16),
            height=2,
            bg="lightgreen",
            command=self.confirm
        ).pack(side="left", expand=True, fill="x", padx=5)

    def add_char(self, c):
        self.var.set(self.var.get() + c)

    def backspace(self):
        self.var.set(self.var.get()[:-1])

    def confirm(self):
        self.result = self.var.get().strip()
        self.destroy()
