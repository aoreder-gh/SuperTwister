# ================================================================================================
# Super Twister 3001
# confirm_overlay.py --- Confirmation overlay for user actions
# @author    Andreas Reder <aoreder@googlemail.com>
# ================================================================================================

import tkinter as tk


class ConfirmOverlay(tk.Frame):

    def __init__(self, parent, message="Are you sure?"):
        super().__init__(parent, bg="#000000")

        self.parent = parent
        self.result = False

        # Vollflächig über Parent legen
        self.place(relx=0, rely=0, relwidth=1, relheight=1)

        # Klicks blockieren
        self.bind("<Button-1>", lambda e: None)

        # Zentrale Dialogbox
        box = tk.Frame(self, bg="white", bd=3, relief="ridge")
        box.place(relx=0.5, rely=0.5, anchor="center", width=500, height=250)

        tk.Label(
            box,
            text=message,
            font=("Arial", 16),
            wraplength=450,
            justify="center",
            bg="white"
        ).pack(pady=20)

        btn_frame = tk.Frame(box, bg="white")
        btn_frame.pack(fill="x", pady=10)

        tk.Button(
            btn_frame,
            text="YES",
            font=("Arial", 18),
            bg="#d9534f",
            fg="white",
            height=2,
            command=self.confirm
        ).pack(side="left", expand=True, fill="x", padx=5)

        tk.Button(
            btn_frame,
            text="NO",
            font=("Arial", 18),
            bg="#5bc0de",
            height=2,
            command=self.close
        ).pack(side="left", expand=True, fill="x", padx=5)

    def confirm(self):
        self.result = True
        self.close()

    def close(self):
        self.destroy()