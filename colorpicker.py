from PIL import Image, ImageDraw
from typing import Callable

import customtkinter as ctk
import colorsys

class ColorPicker(ctk.CTkToplevel):
    def __init__(self, parent: ctk.CTk, callback: Callable, font: tuple, title: str = "Choose a color", *args, **kwargs):
        super().__init__(parent, fg_color="#212121")
        self.callback = callback
        self.args = args
        self.kwargs = kwargs
        self.button1_down = False

        self.WIDTH = 400
        self.HEIGHT = 400

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        self.selected_color = [(255, 255, 255), "#ffffff"]

        x_position = (screen_width - self.WIDTH) // 2
        y_position = (screen_height - self.HEIGHT) // 2

        self.geometry(f"{self.WIDTH}x{self.HEIGHT}+{x_position}+{y_position}")
        self.title(title)
        self.resizable(False, False)

        self.imagergb, self.imagebw = self.generateGradientImage()
        self.photorgb = ctk.CTkImage(light_image=self.imagergb, size=(256, 256))
        self.photobw = ctk.CTkImage(light_image=self.imagebw, size=(40, 256))

        self.holder = ctk.CTkFrame(self, width=self.WIDTH-40, height=270, fg_color="#363636")
        self.holder.place(rely=0.4, relx=0.5, anchor="center")

        self.label = ctk.CTkLabel(self.holder, image=self.photorgb, text="")
        self.label2 = ctk.CTkLabel(self.holder, image=self.photobw, text="")
        self.label.place(relx=0.0, rely=0.5, anchor="w", x=7)
        self.label2.place(relx=1, rely=0.5, anchor="e", x=-7)

        self.colorPreview = ctk.CTkFrame(self, width=self.WIDTH-40, height=40, fg_color="#ffffff")
        self.colorPreview.place(relx=0.5, rely=0.81, anchor="center")

        self.bindEvents(self.label, 0)
        self.bindEvents(self.label2, 1)

        self.button_submit = ctk.CTkButton(self, width=80, height=30, text="Submit", fg_color="#03fc8c", hover_color="#048c4f", font=font, text_color="#000000", command=self.submit)
        self.button_cancel = ctk.CTkButton(self, width=80, height=30, text="Cancel", fg_color="#d10f39", hover_color="#8f0724", font=font, command=self.cancel)

        self.button_submit.place(relx=0.4, rely=0.93, anchor="e")
        self.button_cancel.place(relx=0.6, rely=0.93, anchor="w")

    def bindEvents(self, label: ctk.CTkLabel, id: int):
        label.bind("<Button-1>", lambda event: self.mouse1ButtonDown(event, id))
        label.bind("<ButtonRelease-1>", self.mouse1ButtonUp)
        label.bind("<Motion>", lambda event: self.mouseMotion(event, id))

    def submit(self) -> None:
        func = self.callback
        args = self.args
        kwargs = self.kwargs

        func(self.selected_color, *args, **kwargs)

        self.destroy()

    def cancel(self) -> None:
        self.destroy()

    def generateGradientImage(self) -> list:
        width, height = 256, 256
        imagergb = Image.new("RGB", (width, height), "#000000")
        imagebw = Image.new("RGB", (40, height), "#000000")
        drawrgb = ImageDraw.Draw(imagergb)
        drawbw = ImageDraw.Draw(imagebw)
        
        for x in range(width+1):
            for y in range(height+1):
                hue = x / width

                saturation = 1 - (y / height)

                lightness = 0.5

                r, g, b = colorsys.hls_to_rgb(hue, lightness, saturation)
                
                r = int(r * 255)
                g = int(g * 255)
                b = int(b * 255)

                drawrgb.point((x, y), fill=(r, g, b))

        width = 40

        for x in range(width+1):
            for y in range(height+1):
                drawbw.point((width - x, height - y), fill=(y, y, y))
        
        return imagergb, imagebw
    
    def mouse1ButtonDown(self, event, id: int) -> None:
        self.button1_down = True

        self.bringPointer(event.x, event.y, id)

    def mouse1ButtonUp(self, event) -> None:
        self.button1_down = False
    
    def mouseMotion(self, event, id: int) -> None:
        if self.button1_down:
            self.bringPointer(event.x, event.y, id)


    def bringPointer(self, x: int, y: int, id: int) -> None:
        bounds = {
            0: (0, 255, 0, 255),
            1: (0, 40, 0, 255)
        }

        x_min, x_max, y_min, y_max = bounds[id]
        if x < x_min or x > x_max or y < y_min or y > y_max:
            return
            
        image = [self.imagergb, self.imagebw][id]

        rgb = image.getpixel((x, y))

        self.updateColor(rgb)


    def updateColor(self, rgb: list[int]) -> None:
        hex = f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"
        self.selected_color = [rgb, hex]

        self.colorPreview.configure(fg_color=hex)
