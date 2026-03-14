#  /**
#   * Super Twister 3001
#   *
#   * @author    Andreas Reder <aoreder@gmail.com>
#   *
#   * @copyright Andreas Reder
#   * @version   1.0.0
#   */

import tkinter as tk

class BaseDialog(tk.Toplevel):

    def __init__(self, root, title="Dialog", width=500, height=400):
        super().__init__(root)

        self.root = root
        self.title(title)
        self.geometry(f"{width}x{height}")
        self.resizable(False, False)
        #self.overrideredirect(True)   # no window frame

        # Modal behaviour
        self.transient(root)
        self.grab_set()

        # Center on parent
        self.update_idletasks()
        x = root.winfo_rootx() + (root.winfo_width() // 2) - (width // 2)
        y = root.winfo_rooty() + (root.winfo_height() // 2) - (height // 2)
        self.geometry(f"+{x}+{y}")

        # Main content area
        self.content = tk.Frame(self)
        self.content.pack(expand=True, fill="both", padx=20, pady=(20, 00))

        # Bottom bar for touch close
        bottom_bar = tk.Frame(self, height=60)
        bottom_bar.pack(fill="x", side="bottom")
        bottom_bar.pack_propagate(False)

        btn_close = tk.Button(
            bottom_bar,
            text="Close",
            font=("Arial", 18),
            height=2,
            bg="#ef8f8d",
            fg="white",
            activebackground="#953b39",
            relief="raised",
            bd=4,
            command=self.close
        )

        btn_close.pack(fill="both", expand=True, padx=20, pady=10)

        self.protocol("WM_DELETE_WINDOW", self.close)

    def close(self):
        try:
            self.grab_release()
        except:
            pass
        self.destroy()
