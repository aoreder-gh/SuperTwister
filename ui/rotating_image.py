# ==============================================================
# Super Twister 3001
# class to rotate an image
# @author    Andreas Reder <aoreder@gmail.com>
# ==============================================================  

import customtkinter as ctk
from PIL import Image

class RotatingGear(ctk.CTkLabel):
    def __init__(self, master, path, size=100, step=10, delay=50):
        super().__init__(master, text="")

        self.delay = delay
        self.frames = []
        self.index = 0

        original = Image.open(path).resize((size, size))

        # Frames VORBERECHNEN (einmalig!)
        for angle in range(0, 360, step):
            rotated = original.rotate(angle, resample=Image.BICUBIC)
            img = ctk.CTkImage(light_image=rotated, size=(size, size))
            self.frames.append(img)

        self.animate()

    def animate(self):
        self.configure(image=self.frames[self.index])
        self.index = (self.index + 1) % len(self.frames)
        self.after(self.delay, self.animate)