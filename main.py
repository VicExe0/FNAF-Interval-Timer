from typing import Optional, Callable, Any
from tkextrafont import Font as exFont
from colorpicker import ColorPicker
from tkinter import filedialog
from timer import TimerView

import customtkinter as ctk
import tkinter as tk

import json

import os
os.system("cls")

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("assets/theme.json")
VERSION = "v1.0.1"

def createNavButton(master, width: int, height: int, text: str, font: tuple, command: Callable) -> ctk.CTkButton:
    return ctk.CTkButton(master,
                         width=width, height=height,
                         fg_color="#363636", hover_color="#262626",
                         text=text, font=font,
                         command=command)

class NavFrame(ctk.CTkFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.hover = True

    def mouseEnter(self, event) -> None:
        self.hover = True

    def mouseLeave(self, event) -> None:
        self.hover = False

    def forgetFrame(self) -> None:
        self.place_forget()
        self.hover = True
        self.lift()

    def placeFrame(self, **kwargs) -> None:
        self.place(**kwargs)
        self.bind("<Enter>", self.mouseEnter)
        self.bind("<Leave>", self.mouseLeave)
        self.visible = True

    def __getattr__(self, value: Any) -> Optional[Any]:
        if value in self.__dict__:
            return self.__dict__[value]
        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{value}'")

class NavSubButton(ctk.CTkButton):
    def __init__(self, master, width: int, height: int, text: str, font: tuple, command: Callable) -> None:
        super().__init__(master, width=width, height=height, text=text, font=font, command=command, anchor="w", fg_color="#363636", hover_color="#262626")


class App(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()
        self.WIDTH = 400
        self.HEIGHT = 500

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        x_position = (screen_width - self.WIDTH) // 2
        y_position = (screen_height - self.HEIGHT) // 2

        self.geometry(f"{self.WIDTH}x{self.HEIGHT}+{x_position}+{y_position}")
        self.iconbitmap("assets/images/favicon.ico")
        self.resizable(False, False)
        self.title("FNAF Interval Timer by VicExe")
        
        self.currentNavFrame = None
        self.timerWindow = None
        self.currentScreen = 0

        self.bind("<Button-1>", self.mouse1ButtonDown)

        if not self.loadFonts():
            print("Error: Failed to load fonts. Default fonts used instead")

        if not self.loadWidgets():
            print("Error: Failed to load widgets.")
            return

    def start(self) -> None:
        self.mainloop()

    def mouse1ButtonDown(self, event) -> None:
        if self.currentNavFrame and not self.isMouseInsideFrame(event, self.currentNavFrame):
            self.currentNavFrame.forgetFrame()
            self.currentNavFrame = None

    def isMouseInsideFrame(self, event, frame) -> bool:
        x, y, width, height = frame.bbox()
        inside_frame = x <= event.x <= x + width and y <= event.y <= y + height
        
        return inside_frame or event.y < 24
        
    def loadFonts(self) -> bool:
        try:
            self.LCD_SOLID = "LCD Solid"
            self.CONSOLAS_REGULAR = "Consolas Regular"

            exFont(file="assets/fonts/LcdSolid-VPzB.ttf", family=self.LCD_SOLID)
            exFont(file="assets/fonts/Consolas-Regular.ttf", family=self.CONSOLAS_REGULAR)

            return True
        
        except Exception as e:
            self.LCD_SOLID = "Helvetica"
            self.CONSOLAS_REGULAR = "Helvetica"

            return False
        
    def showNavFrame(self, id: int) -> None: # Button Action
        for frame in self.nav_frames:
            frame.forgetFrame()

        pos = {
            0: 0,
            1: 50,
            2: 120,
            3: 180
        }.get(id, 0)

        frame = self.nav_frames[id]
        frame.placeFrame(x=pos, y=24) # NAVBAR_HEIGHT
        self.currentNavFrame = frame

    def saveConfig(self) -> None: # Button Action
        file_path = filedialog.asksaveasfilename(
            title="Save config",
            defaultextension=".json",
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")]
        )

        if file_path is None:
            print("Failed to get file path.")
            return
        
        print(file_path)

    def loadConfig(self) -> None: # Button Action
        file_path = filedialog.askopenfilename(
            title="Save config",
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")]
        )

        if file_path is None:
            print("Failed to get file path.")
            return
        
        print(file_path)

    def changeView(self, id: int) -> None: # Button Action
        for view in self.view_frames:
            view.place_forget()

        self.view_frames[id].place(x=0, y=24) # NAVBAR_HEIGHT
        self.currentNavFrame.forgetFrame()
        self.currentNavFrame = None

    def toggleTimerWindow(self) -> None:
        self.currentNavFrame.forgetFrame()
        self.currentNavFrame = None

        if not self.timerWindow is None:
            self.timerWindow.destroyWindow()
            self.timerWindow = None
            return
        
        self.timerWindow = TimerView(self, settings_path="assets/presets/test.json")
        self.timerWindow.createWindow()


    def loadWidgets(self) -> bool:
        WIDTH, HEIGHT = self.WIDTH, self.HEIGHT

        try:
            NAVBAR_HEIGHT = 24
            self.nav_bar = ctk.CTkFrame(self, width=WIDTH, height=NAVBAR_HEIGHT, fg_color="#292929")
            self.nav_bar.place(x=0, y=0)

            self.nav_version_label = ctk.CTkLabel(self.nav_bar, text=VERSION, font=(self.CONSOLAS_REGULAR, 14), text_color="#595959")
            self.nav_version_label.place(relx=1.0, rely=0.5, anchor="e", x=-5)

            consolas_regular15 = (self.CONSOLAS_REGULAR, 15)

            self.nav_file = createNavButton(self.nav_bar, width=50, height=NAVBAR_HEIGHT, text="File", font=consolas_regular15, command=lambda: self.showNavFrame(0))
            self.nav_settings = createNavButton(self.nav_bar, width=70, height=NAVBAR_HEIGHT, text="Settings", font=consolas_regular15, command=lambda: self.showNavFrame(1))
            self.nav_help = createNavButton(self.nav_bar, width=60, height=NAVBAR_HEIGHT, text="Help", font=consolas_regular15, command=lambda: self.showNavFrame(2))
            
            self.nav_file_frame = NavFrame(self, width=120, height=90, fg_color="#363636")
            self.nav_settings_frame = NavFrame(self, width=120, height=60, fg_color="#363636")
            self.nav_help_frame = NavFrame(self, width=120, height=90, fg_color="#363636")
            
            self.nav_frames = [self.nav_file_frame, self.nav_settings_frame, self.nav_help_frame]

            self.nav_file.place(x=0, y=0)
            self.nav_settings.place(x=50, y=0)
            self.nav_help.place(x=120, y=0)

            self.nav_file_save = NavSubButton(self.nav_file_frame, 120, 30, "Save", consolas_regular15, self.saveConfig)
            self.nav_file_load = NavSubButton(self.nav_file_frame, 120, 30, "Load", consolas_regular15, self.loadConfig)
            self.nav_file_loadpreset = NavSubButton(self.nav_file_frame, 120, 30, "Load preset", consolas_regular15, lambda: self.changeView(2))
            self.nav_settings_change = NavSubButton(self.nav_settings_frame, 120, 30, "Change settings", consolas_regular15, lambda: self.changeView(1))
            self.nav_settings_sstimer = NavSubButton(self.nav_settings_frame, 120, 30, "Start/Stop timer", consolas_regular15, self.toggleTimerWindow)
            self.nav_help_about = NavSubButton(self.nav_help_frame, 120, 30, "About", consolas_regular15, lambda: self.changeView(3))
            self.nav_help_git = NavSubButton(self.nav_help_frame, 120, 30, "My Github", consolas_regular15, lambda: print("My Github"))
            self.nav_help_htu = NavSubButton(self.nav_help_frame, 120, 30, "How to use", consolas_regular15, lambda: self.changeView(4))

            self.nav_file_save.place(x=0, y=0)
            self.nav_file_load.place(x=0, y=30)
            self.nav_file_loadpreset.place(x=0, y=60)
            self.nav_settings_change.place(x=0, y=0)
            self.nav_settings_sstimer.place(x=0, y=30)
            self.nav_help_about.place(x=0, y=0)
            self.nav_help_git.place(x=0, y=30)
            self.nav_help_htu.place(x=0, y=60)

            self.view_timers = ctk.CTkFrame(self, width=WIDTH, height=HEIGHT-NAVBAR_HEIGHT)
            self.view_settings = ctk.CTkFrame(self, width=WIDTH, height=HEIGHT-NAVBAR_HEIGHT)
            self.view_load_presets = ctk.CTkFrame(self, width=WIDTH, height=HEIGHT-NAVBAR_HEIGHT)
            self.view_about = ctk.CTkFrame(self, width=WIDTH, height=HEIGHT-NAVBAR_HEIGHT)
            self.view_htu = ctk.CTkFrame(self, width=WIDTH, height=HEIGHT-NAVBAR_HEIGHT)

            self.view_frames = [self.view_timers, self.view_settings, self.view_load_presets, self.view_about, self.view_htu]

            self.view_timers.place(x=0, y=24)

            




            return True

        except Exception as e:
            print(e)
            return False
        

def main() -> None:
    app = App()
    app.start()


if __name__ == "__main__":
    main()