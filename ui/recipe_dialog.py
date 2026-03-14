# ================================================================================================
# Super Twister 3001
# receipe_editor.py --- Dialog to edit receipe profile settings
# @author    Andreas Reder <aoreder@googlemail.com>
# ================================================================================================


import tkinter as tk
import os
import shutil
import configs.language as language
import state
from configs.config import RECIPE_DIR
from logic.recipes import list_recipes, load_recipe, save_recipe
from ui.base_dialog import BaseDialog
from ui.confirm_overlay import ConfirmOverlay

class RecipeDialog(BaseDialog):

    def __init__(self, root, mode="load"):
        super().__init__(
            root,
            title=language.texts[state.language]["recipe"],
            width=960,
            height=560
        )
        self.update_idletasks()
        x = self.winfo_x()
        self.geometry(f"+{x}+0")

        self.mode = mode
        self.caps = False
        self.shift = False
        self.key_buttons = []

        self.build_ui()

    # -------------------------------------------------
    # UI
    # -------------------------------------------------

    def build_ui(self):
        if self.mode == "load":
            self.build_load()
        else:
            self.build_save()

    def build_load(self):

        self.search_var = tk.StringVar()

        # --- SEARCH FIELD ---
        search_frame = tk.Frame(self.content)
        search_frame.pack(fill="x", pady=5)

        search_entry = tk.Entry(
            search_frame,
            textvariable=self.search_var,
            font=("Arial", 16),
            justify="center"
        )
        search_entry.pack(side="left", fill="x", expand=True, padx=5)

        search_entry.bind("<Button-1>", lambda e: self.open_search_keyboard())

        tk.Button(
            search_frame,
            text="Search",
            font=("Arial", 14),
            command=self.refresh_recipe_list
        ).pack(side="right", padx=5)

        # --- SCROLL AREA ---
        container = tk.Frame(self.content)
        container.pack(expand=True, fill="both")

        canvas = tk.Canvas(container)
        canvas.bind("<ButtonPress-1>", lambda e: canvas.scan_mark(e.x, e.y))
        canvas.bind("<B1-Motion>", lambda e: canvas.scan_dragto(e.x, e.y, gain=1))
        scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview, width=40)
        self.scroll_frame = tk.Frame(canvas)

        self.scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.canvas = canvas

        self.refresh_recipe_list()

    # -------------------------------------------------
    # SAVE MODE WITH KEYBOARD
    # -------------------------------------------------

    def build_save(self):

        self.filename = tk.StringVar(value=state.current_profile)

        self.entry = tk.Entry(
            self.content,
            textvariable=self.filename,
            font=("Arial", 24),
            justify="center"
        )
        self.entry.pack(fill="x", pady=10)

        self.msg = tk.Label(self.content, font=("Arial", 14))
        self.msg.pack(pady=5)
        self.msg.config(
            text=str(state.target_rpm) + " rpm|" + str(state.remaining_turns) + " turns|" + ("CW" if state.direction else "CCW") + "|" + ("twist" if state.twist_mode else "noTwist"),
            fg="black"
        )

        self.build_keyboard()

        tk.Button(
            self.content,
            text="Close",
            font=("Arial", 18),
            height=2,
            width=30,
            bg="#d9534f",
            fg="white",
            activebackground="#c9302c",
            command=self.close
        ).pack(side="left", padx=10)
        
        tk.Button(
            self.content,
            text="Save",
            font=("Arial", 18),
            height=2,
            width=30,
            bg="#5bc0de",
            fg="white",
            activebackground="#98C4F3",
            command=self.save_recipes
        ).pack(side="right", padx=10)

            
    def refresh_recipe_list(self):

        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        recipes = list_recipes()

        # --- SORT A-Z ---
        recipes.sort(key=lambda x: x.lower())

        # --- FILTER ---
        search = self.search_var.get().lower()
        if search:
            recipes = [r for r in recipes if search in r.lower()]

        if not recipes:
            tk.Label(
                self.scroll_frame,
                text="No recipes found",
                font=("Arial", 16)
            ).pack(pady=20)
            return

        # --- DYNAMIC COLUMNS ---
        width = self.winfo_width()

        if width >= 1000:
            cols = 3
        elif width >= 700:
            cols = 2
        else:
            cols = 1

        for i, filename in enumerate(recipes):

            data = load_recipe(filename)

            row_frame = tk.Frame(self.scroll_frame)
            row_frame.grid(row=i // cols,
                        column=i % cols,
                        padx=15,
                        pady=5,
                        sticky="nsew")

            # Button text with RPM + Turns + Direction + Twist Mode
            btn_text = (
                f"{data['name']}\n"
                f"{int(data['rpm'])}rpm|"
                f"{int(data['turns'])} turns|"
                f"{data['direction'].upper()}|"
                f"{'twist' if data.get('twist_mode') else 'noTwist'}"
            )

            tk.Button(
                row_frame,
                text=btn_text,
                font=("Arial", 16),
                height=2,
                width=24,
                justify="center",
                command=lambda d=data: self.load_recipe(d)
            ).pack(side="left")

            tk.Button(
                row_frame,
                text="X",
                font=("Arial", 14),
                fg="white",
                bg="#d9534f",
                width=3,
                command=lambda f=filename: self.delete_recipe(f)
            ).pack(side="left", padx=5)

    def delete_recipe(self, filename):

        # Overlay erstellen
        overlay = ConfirmOverlay(
            self,
            message=f"Move recipe '{filename.replace('.json','')}' to deleted?"
        )

        # Warten bis Overlay geschlossen
        self.wait_window(overlay)

        if not overlay.result:
            return

        deleted_dir = os.path.join(RECIPE_DIR, "deleted")
        os.makedirs(deleted_dir, exist_ok=True)

        shutil.move(
            os.path.join(RECIPE_DIR, filename),
            os.path.join(deleted_dir, filename)
        )

        self.refresh_recipe_list()

    def open_search_keyboard(self):

        from ui.keyboard_dialog import KeyboardDialog

        kb = KeyboardDialog(self, self.search_var.get())
        self.wait_window(kb)

        if kb.result is not None:
            self.search_var.set(kb.result)
            self.refresh_recipe_list()

    # -------------------------------------------------
    # KEYBOARD
    # -------------------------------------------------

    def build_keyboard(self):

        kb = tk.Frame(self.content)
        kb.pack(expand=True)

        self.layout = [
            list("1234567890"),
            list("QWERTZUIOP"),
            list("ASDFGHJKL"),
            list("YXCVBNM-_")
        ]

        for row in self.layout:
            row_frame = tk.Frame(kb)
            row_frame.pack()

            for key in row:
                btn = tk.Button(
                    row_frame,
                    text=key,
                    font=("Arial", 18),
                    width=4,
                    height=2,
                    bg="#eeeeee",
                    command=lambda c=key: self.add_char(c)
                )
                btn.pack(side="left", padx=3, pady=3)
                self.key_buttons.append(btn)

        # --- Special Keys ---
        bottom = tk.Frame(kb)
        bottom.pack(fill="x", pady=10)

        # Linke Gruppe
        left_frame = tk.Frame(bottom)
        left_frame.pack(side="left")

        self.shift_btn = tk.Button(
            left_frame,
            text="Shift",
            font=("Arial", 16),
            width=6,
            command=self.activate_shift
        )
        self.shift_btn.pack(side="left", padx=5)

        self.caps_btn = tk.Button(
            left_frame,
            text="Caps",
            font=("Arial", 16),
            width=6,
            command=self.toggle_caps
        )
        self.caps_btn.pack(side="left", padx=5)


        # Rechte Gruppe
        right_frame = tk.Frame(bottom)
        right_frame.pack(side="right")

        tk.Button(
            right_frame,
            text="Back",
            font=("Arial", 16),
            width=6,
            command=self.backspace
        ).pack(side="right", padx=5)

        tk.Button(
            right_frame,
            text="Clear",
            font=("Arial", 16),
            width=6,
            command=lambda: [self.filename.set(""), self.entry.icursor(tk.END)]
            
        ).pack(side="right", padx=5)

    # -------------------------------------------------
    # KEYBOARD LOGIC
    # -------------------------------------------------

    def update_key_labels(self):
        for btn in self.key_buttons:
            char = btn["text"]
            if char.isalpha():
                if self.caps or self.shift:
                    btn.config(text=char.upper())
                else:
                    btn.config(text=char.lower())

        # LED Style
        self.caps_btn.config(
            bg="#5cb85c" if self.caps else "#f0f0f0"
        )
        self.shift_btn.config(
            bg="#5cb85c" if self.shift else "#f0f0f0"
        )

    def add_char(self, char):

        if char.isalpha():
            if self.caps or self.shift:
                char = char.upper()
            else:
                char = char.lower()

        self.filename.set(self.filename.get() + char)
        # Cursor ans Ende setzen
        self.entry.icursor(tk.END)

        if self.shift:
            self.shift = False
            self.update_key_labels()

    def backspace(self):
        self.filename.set(self.filename.get()[:-1])
        self.entry.icursor(tk.END)

    def toggle_caps(self):
        self.caps = not self.caps
        self.update_key_labels()

    def activate_shift(self):
        self.shift = True
        self.update_key_labels()

    # -------------------------------------------------
    # ACTIONS
    # -------------------------------------------------

    def load_recipe(self, d):
        state.target_rpm = d["rpm"]
        state.remaining_turns = d["turns"]
        state.current_profile = d["name"]
        state.direction = True if d["direction"] == "cw" else False
        state.twist_mode = d.get("twist_mode", False)
        state.loaded_rpm = d["rpm"]
        state.loaded_turns = d["turns"]
        self.close()

    def save_recipes(self):
        name = self.filename.get().strip()
        t = language.texts[state.language]
        if not name:
            self.msg.config(
                text=language.texts[state.language]["name_missing"],
                fg="red"
            )
            return

        # Validate allowed characters
        allowed = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_"
        if any(c not in allowed for c in name):
            self.msg.config(
                text=t["invalidchar"],
                fg="red"
            )
            return

        # Duplicate check
        existing = [r.replace(".json", "") for r in list_recipes()]
        if name in existing:
            self.msg.config(
                text=t["doublercp"],
                fg="red"
            )
            return

        save_recipe(name)
        self.close()
