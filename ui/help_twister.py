# ==============================================================
# Super Twister 3001
# help_twister.py --- Help dialog for twister operations
# @author    Andreas Reder <aoreder@googlemail.com>
# ==============================================================

import tkinter as tk
from tkinter import ttk
import json
import os
import state
import configs.language as language

from ui.base_dialog import BaseDialog
from PIL import features, Image, ImageTk

class HelpTwisterDialog(BaseDialog):

    def __init__(self, root):
        super().__init__(
            root,
            title=language.texts[state.language]["helpwizard"],
            width=1020,
            height=560
        )
        self.update_idletasks()
        x = self.winfo_x()
        self.geometry(f"+{x}+0")

        self.current_step = 0
        self.steps = []
        self.help_type = None
        self.config_data = self.load_config()
        
        self.build_wizard()
        
        if state.wizard_active and state.wizard_help_type:
            self.resume_wizard()
        else:
            self.show_help_selection()
            
    # -------------------------------------------------
    # CONFIG LOAD
    # -------------------------------------------------

    def load_config(self):
        path = os.path.join("configs", "help_st.json")
        try:
            with open(path, "r") as f:
                return json.load(f)
        except Exception as e:
            tk.messagebox.showerror("Error", f"Helper configuration error:\n{e}")
            return {}

    # -------------------------------------------------
    # RESUME LOADER
    # -------------------------------------------------

    def resume_wizard(self):
        self.help_type = state.wizard_help_type
        self.steps = self.config_data[self.he_type]["steps"]
        self.current_step = state.wizard_step_index
        self.show_step()

    # -------------------------------------------------
    # BUILD WIZARD LAYOUT
    # -------------------------------------------------

    def build_wizard(self):
        
        t = language.texts[state.language]
        # ---------- HEADER ----------
        self.header_frame = tk.Frame(self.content, bg="#2c3e50", height=120)
        self.header_frame.pack(fill="x")
        self.header_frame.pack_propagate(False)

        self.title_label = tk.Label(
            self.header_frame,
            text="",
            font=("Arial", 22, "bold"),
            fg="white",
            bg="#2c3e50"
        )
        self.title_label.pack(pady=10)

        self.step_label = tk.Label(
            self.header_frame,
            text="",
            font=("Arial", 16),
            fg="white",
            bg="#2c3e50"
        )
        self.step_label.pack()

        self.reset_btn = tk.Button(
            self.header_frame,
            text="⟲ Reset",
            font=("Arial", 12),
            bg="#34495e",
            fg="white",
            relief="flat",
            command=self.reset_wizard
        )
        self.reset_btn.place(
            relx=1.0,
            rely=0.0,
            x=-10,
            y=10,
            anchor="ne"
        )

        self.reset_btn.place_forget()

        self.progress = ttk.Progressbar(
            self.header_frame,
            orient="horizontal",
            mode="determinate",
            maximum=100,
            length=600
        )
        self.progress.pack(pady=10)

        style = ttk.Style()
        style.theme_use("default")
        style.configure(
            "Custom.Horizontal.TProgressbar",
            thickness=15
        )
        self.progress.config(style="Custom.Horizontal.TProgressbar")

        # ---------- CONTENT ----------
        self.page_frame = tk.Frame(self.content, bg="#ecf0f1")
        self.page_frame.pack(expand=True, fill="both")
        
        self.content.pack_propagate(False)
        self.content.update_idletasks()
        self.content.configure(height=self.winfo_height() - 120)

        # ---------- NAV ----------
        self.nav_frame = tk.Frame(self.content, height=60)
        self.nav_frame.pack(fill="x")
        self.nav_frame.pack_propagate(False)

        self.btn_back = tk.Button(
            self.nav_frame,
            text=t["back"],
            font=("Arial", 16),
            height=2,
            width=12,
            bg="#bdc3c7",
            relief="raised",
            bd=4,
            command=self.prev_step
        )
        self.btn_back.pack(side="left", padx=10, pady=5)

        self.done_var = tk.BooleanVar()

        self.done_check = tk.Checkbutton(
            self.nav_frame,
            text=t["helpCompleted"],
            font=("Arial", 16, "bold"),
            variable=self.done_var,
            bg=self.nav_frame.cget("bg"),
            activebackground=self.nav_frame.cget("bg")
        )
        self.done_check.pack(side="left", expand=True)

        self.done_var.trace_add("write", self._on_done_changed)

        self.btn_next = tk.Button(
            self.nav_frame,
            text=t["next"],
            font=("Arial", 16),
            height=2,
            width=12,
            bg="DarkOliveGreen1",
            activebackground="DarkOliveGreen1",
            fg="white",
            relief="raised",
            bd=4,
            command=self.next_step
        )
        self.btn_next.pack(side="right", padx=10, pady=5)

        self.show_help_selection()

    # -------------------------------------------------
    # RESET WIZARD
    # -------------------------------------------------

    def reset_wizard(self):
        t = language.texts[state.language]
        if not tk.messagebox.askyesno(title=t["unsafe"], message=t["help_reset"], parent=self):
            return

        # reset global wizard state
        state.wizard_active = False
        state.wizard_help_type = None
        state.wizard_step_index = 0
        state.wizard_completed_steps.clear()

        # reset dialog state
        self.current_step = 0
        self.help_type = None
        self.steps = []

        # reset checkbox
        self.done_var.set(False)

        # disable navigation
        self.btn_next.config(state="disabled")
        self.btn_back.config(state="disabled")
        self.done_check.config(state="disabled")

        # reset_btn is hidden in show_help_selection, so no need to disable it here
        self.reset_btn.place_forget()

        # show bow selection again
        self.show_help_selection()

    # -------------------------------------------------
    # DONE CHECKBOX CHANGE
    # -------------------------------------------------

    def _on_done_changed(self, *args):
        if not self.help_type:
            return

        key = f"{self.help_type}_{self.current_step}"
        state.wizard_completed_steps[key] = self.done_var.get()

        step = self.steps[self.current_step]
        icon = "✔ " if self.done_var.get() else "✖ "
        self.title_label.config(text=icon + self.tr(step["title"]))

        # animate header color when step completion changes
        if self.done_var.get():
            self.animate_header_color("#27ae60")   # green
        else:
            self.animate_header_color("#e74c3c")   # red
        self.update_next_button()
        
    # -------------------------------------------------
    # BOW SELECTION
    # -------------------------------------------------

    def show_help_selection(self):
        self.clear_page()

        t = language.texts[state.language]

        self.title_label.config(text=t["chooseHelpArea"])
        self.step_label.config(text="")
        self.progress["value"] = 0

        # --- Container ---
        container = tk.Frame(self.page_frame, bg="#ecf0f1")
        container.pack(fill="both", expand=True)

        canvas = tk.Canvas(container, bg="white", highlightthickness=0)
        scrollbar = tk.Scrollbar(
            container,
            orient="vertical",
            command=canvas.yview,
            #style="Dialog.Vertical.TScrollbar"
            width=40
        )

        scroll_frame = tk.Frame(canvas, bg="white")

        window_id = canvas.create_window((0, 0), window=scroll_frame, anchor="nw")

        # Scrollregion anpassen
        def on_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        scroll_frame.bind("<Configure>", on_configure)

        # Breite automatisch anpassen
        def resize_scroll_frame(event):
            canvas.itemconfig(window_id, width=event.width)

        canvas.bind("<Configure>", resize_scroll_frame)

        # Touch-Scroll (Finger ziehen)
        def on_press(event):
            canvas.scan_mark(event.x, event.y)

        def on_drag(event):
            canvas.scan_dragto(event.x, event.y, gain=1)

        canvas.bind("<ButtonPress-1>", on_press)
        canvas.bind("<B1-Motion>", on_drag)

        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # --- Inhalt ---
        tk.Label(
            scroll_frame,
            text=t["helpQuestion"],
            font=("Arial", 20),
            bg="white"
        ).pack(pady=20)

        for key, value in self.config_data.items():
            tk.Button(
                scroll_frame,
                text=self.tr(value["display_name"]),
                font=("Arial", 18),
                height=2,
                bg="#3498db",
                fg="white",
                command=lambda k=key: self.start_wizard(k)
            ).pack(fill="x", padx=40, pady=10)

        self.btn_back.config(state="disabled")
        self.btn_next.config(state="disabled")
        
        self.done_check.config(state="disabled")
        #self.done_var = None

    # -------------------------------------------------
    # START WIZARD
    # -------------------------------------------------

    def start_wizard(self, bow_key):
        
        state.wizard_active = True
        state.wizard_help_type = bow_key
        state.wizard_step_index = 0
        self.help_type = bow_key
        self.steps = self.config_data[bow_key]["steps"]
        self.current_step = 0

        self.btn_back.config(state="normal")
        self.btn_next.config(state="normal")
        
        self.done_check.config(state="normal")

        self.reset_btn.place(relx=1.0, rely=0.0, x=-10, y=10, anchor="ne")

        self.show_step()

    # -------------------------------------------------
    # SHOW STEP
    # -------------------------------------------------

    def show_step(self):
        self.clear_page()
        t = language.texts[state.language]
        if self.current_step == 0:
            self._apply_header_color("#e74c3c")
        state.wizard_step_index = self.current_step
        step = self.steps[self.current_step]

        key = f"{self.help_type}_{self.current_step}"
        completed = state.wizard_completed_steps.get(key, False)

        total = len(self.steps)
        percent = int((self.current_step + 1) / total * 100)

        # ---------- HEADER ----------
        if completed:
            color = "#27ae60"
            icon = "✔ "
        else:
            color = "#e74c3c"
            icon = "✖ "

        self.animate_header_color(color)

        self.title_label.config(text=icon + self.tr(step["title"]))
        self.step_label.config(
            text=t["helperLabel"].format(
                current=self.current_step + 1,
                total=total
            )
        )

        self.progress_target = percent
        self.animate_progress(self.progress_target)


        # ---------- SCROLL CONTAINER ----------
        container = tk.Frame(self.page_frame, bg="#ecf0f1")
        container.pack(fill="both", expand=True)

        canvas = tk.Canvas(container, bg="white", highlightthickness=0)
        scrollbar = tk.Scrollbar(
            container,
            orient="vertical",
            command=canvas.yview,
            width=40
        )

        scroll_frame = tk.Frame(canvas, bg="white")

        window_id = canvas.create_window((0, 0), window=scroll_frame, anchor="nw")

        def on_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        scroll_frame.bind("<Configure>", on_configure)

        def resize_scroll_frame(event):
            canvas.itemconfig(window_id, width=event.width)

        canvas.bind("<Configure>", resize_scroll_frame)

        # Touch scroll
        def on_press(event):
            canvas.scan_mark(event.x, event.y)

        def on_drag(event):
            canvas.scan_dragto(event.x, event.y, gain=1)

        canvas.bind("<ButtonPress-1>", on_press)
        canvas.bind("<B1-Motion>", on_drag)

        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # ---------- CONTENT ----------
        tk.Label(
            scroll_frame,
            text=self.tr(step["desc"]),
            font=("Arial", 20),
            bg="white",
            wraplength=900,
            justify="center"
        ).pack(pady=10, padx=20)
        
        # ---------- OPTIONAL IMAGE ----------
        if "image" in step:
            try:
                import os
                # Determine project root directory (two levels above /ui/)
                base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                base_path = os.path.join(
                        base_dir,
                        "img",
                        "help",
                        self.help_type
                )

                img_path = os.path.join(base_path, step["image"])
                img = Image.open(img_path).convert("RGB")

                # Automatically scale image to fit window width
                max_width = self.page_frame.winfo_width() - 460
                ratio = max_width / img.width
                new_size = (
                    int(img.width * ratio),
                    int(img.height * ratio)
                )

                img = img.resize(new_size, Image.LANCZOS)
                self.step_image = ImageTk.PhotoImage(img)

                img_label = tk.Label(
                    scroll_frame,
                    image=self.step_image,
                    bg="white",
                    cursor="hand2"
                )
                img_label.pack(pady=10)

                img_label.bind("<Button-1>", lambda e: self.open_image_zoom(img_path))
                
            except Exception as e:
                print("Could not load the picture:", img_path)
                print("Error:", repr(e))  
        
        # Temporarily disable trace during programmatic update
        info = self.done_var.trace_info()
        if info:
            self.done_var.trace_remove("write", info[0][1])
        self.done_var.set(completed)
        self.done_var.trace_add("write", self._on_done_changed)

        if self.current_step == total - 1:
            self.btn_next.config(text=t["finish"])
        else:
            self.btn_next.config(text=t["next"])
        
        self.done_check.config(state="normal" if self.current_step >= 0 else "disabled")
            
        self.update_next_button()

        self.btn_back.config(
            state="normal" if self.current_step > 0 else "disabled"
        )
        if self.current_step > 0:
            self.reset_btn.place(relx=1.0, rely=0.0, x=-10, y=10, anchor="ne")

    def open_image_zoom(self, img_path):
        zoom = tk.Toplevel(self)
        zoom.geometry("1024x150+0+30")
        zoom.overrideredirect(True)   # no window frame
        zoom.attributes("-topmost", True)

        try:
            img = Image.open(img_path)
            img = img.resize((1024, 150), Image.LANCZOS)
            zoom_image = ImageTk.PhotoImage(img)

            lbl = tk.Label(zoom, image=zoom_image, bg="black")
            lbl.image = zoom_image
            lbl.pack(fill="both", expand=True)

            # Close zoom window on touch
            lbl.bind("<Button-1>", lambda e: zoom.destroy())

        except Exception as e:
            print("Zoom picture error:", e)
                
    def update_next_button(self):
        if self.done_var.get():
            self.btn_next.config(state="normal", fg="black")
        else:
            self.btn_next.config(state="disabled",fg="white")

    # -------------------------------------------------
    # NAVIGATION
    # -------------------------------------------------

    def next_step(self):
        # No checkbox on selection page
        if not hasattr(self, "done_var") or self.done_var is None:
            return

        if not self.done_var.get():
            t = language.texts[state.language]
            tk.messagebox.showwarning(t["info"], t["help_step"])
            return

        if self.current_step < len(self.steps) - 1:
            self.current_step += 1
            self.show_step()
        else:
            state.wizard_active = False
            state.wizard_help_type = None
            state.wizard_step_index = 0
            self.close()

    def prev_step(self):
        if self.current_step > 0:
            self.current_step -= 1
            self.show_step()

    def tr(self, data):
        return data.get(state.language, data.get("DE"))

    # -------------------------------------------------
    # UTILITY FUNCTIONS
    # -------------------------------------------------

    def clear_page(self):
        for widget in self.page_frame.winfo_children():
            widget.destroy()

    # -------------------------------------------------
    # HEADER COLOR ANIMATION
    # -------------------------------------------------

    def animate_header_color(self, target_color):

        def hex_to_rgb(h):
            h = h.lstrip("#")
            return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

        def rgb_to_hex(rgb):
            return "#%02x%02x%02x" % rgb

        start = hex_to_rgb(self.header_frame.cget("bg"))
        end = hex_to_rgb(target_color)

        steps = 10

        for i in range(steps + 1):
            r = int(start[0] + (end[0] - start[0]) * i / steps)
            g = int(start[1] + (end[1] - start[1]) * i / steps)
            b = int(start[2] + (end[2] - start[2]) * i / steps)

            color = rgb_to_hex((r, g, b))

            self.after(
                i * 20,
                lambda c=color: self._apply_header_color(c)
            )

    def _apply_header_color(self, color):
        self.header_frame.config(bg=color)
        self.title_label.config(bg=color)
        self.step_label.config(bg=color)

    # -------------------------------------------------
    # PROGRESS BAR ANIMATION
    # -------------------------------------------------

    def animate_progress(self, target):

        if target != self.progress_target:
            return

        current = float(self.progress["value"])

        diff = target - current

        if abs(diff) < 0.5:
            self.progress["value"] = target
            return

        new_value = current + diff * 0.2

        self.progress["value"] = new_value

        self.after(20, lambda: self.animate_progress(target))