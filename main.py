from timer import TimerView, validateConfigDict
from typing import Optional, Callable, Any
from tkextrafont import Font as exFont
from colorpicker import ColorEntry
from tkinter import filedialog

import customtkinter as ctk

import webbrowser
import json

import os
os.system("cls")

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("assets/theme.json")

VERSION = "v1.0.1"
GITHUB_URL = "https://github.com/VicExe0/FNAF-Interval-Timer"

def createNavButton(master, width: int, height: int, text: str, font: tuple, command: Callable) -> ctk.CTkButton:
    return ctk.CTkButton(master,
                         width=width, height=height,
                         fg_color="#363636", hover_color="#262626",
                         text=text, font=font,
                         command=command)

def createBackButton(master, font: tuple, command: Callable) -> ctk.CTkButton:
    button = ctk.CTkButton(master, text="Back", font=font, width=30, fg_color="transparent", hover_color="#292929", command=command)
    button.place(relx=0.0, rely=1.0, anchor="sw", x=5, y=-5)

    return button


def createTitle(master, title: str, font: tuple) -> ctk.CTkLabel:
    label = ctk.CTkLabel(master, text=title, font=font)
    label.place(relx=0.5, y=20, anchor="center")

    return label

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
        self.title("FNaF Interval Timer by VicExe")
        
        self.currentNavFrame = None
        self.timerWindow = None
        self.currentScreen = 0
        self.choosedPreset = "FNaF 1"

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
            self.closeNavBarFrame()

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
        
    def openGithub(self) -> None: # Button Action
        self.closeNavBarFrame()
        webbrowser.open(GITHUB_URL)
        
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
        
        try:
            data = self.getConfigData()
        
            with open(file_path, "w") as file:
                json.dump(data, file, indent=4)

        except Exception as e:
            # Failed to save file logic
            
            return

    def loadConfig(self) -> None: # Button Action
        file_path = filedialog.askopenfilename(
            title="Load config",
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")]
        )

        if file_path is None:
            print("Failed to get file path.")
            return
        
        try:
            with open(file_path, "r") as file:
                data = json.load(file)

            if not validateConfigDict(data):
                print("Config file is corrupted or incorrect.")
                return
            
            self.loadInConfigData(data)

        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Settings file error: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")

    def changeView(self, id: int) -> None: # Button Action
        for view in self.view_frames:
            view.place_forget()

        self.view_frames[id].place(relx=0.5, rely=0.5, anchor="center", y=12) # NAVBAR_HEIGHT
        self.closeNavBarFrame()

    def closeNavBarFrame(self) -> None:
        if not self.currentNavFrame is None:
            self.currentNavFrame.forgetFrame()
            self.currentNavFrame = None

    def toggleTimerWindow(self) -> None:
        self.closeNavBarFrame()

        if not self.timerWindow is None:
            self.timerWindow.destroyWindow()
            self.timerWindow = None
            return
        
        # data = self.getConfigData()
        # self.timerWindow = TimerView(self, config_data=data)

        self.timerWindow = TimerView(self, config_path="assets/presets/test.json")
        self.timerWindow.createWindow()

    def changePreset(self, choose) -> None:
        self.choosedPreset = choose


    def loadWidgets(self) -> bool:
        WIDTH, HEIGHT = self.WIDTH, self.HEIGHT

        try:
            NAVBAR_HEIGHT = 24
            view_height = HEIGHT-NAVBAR_HEIGHT-20
            view_width = WIDTH-20
            consolas_regular15 = (self.CONSOLAS_REGULAR, 15)
            consolas_regular24 = (self.CONSOLAS_REGULAR, 24)

            self.nav_bar = ctk.CTkFrame(self, width=WIDTH, height=NAVBAR_HEIGHT, fg_color="#292929")
            self.nav_version_label = ctk.CTkLabel(self.nav_bar, text=VERSION, font=(self.CONSOLAS_REGULAR, 14), text_color="#595959")

            self.nav_bar.place(x=0, y=0)
            self.nav_version_label.place(relx=1.0, rely=0.5, anchor="e", x=-5)

            self.nav_file_frame = NavFrame(self, width=120, height=90, fg_color="#363636")
            self.nav_settings_frame = NavFrame(self, width=120, height=60, fg_color="#363636")
            self.nav_help_frame = NavFrame(self, width=120, height=90, fg_color="#363636")
            
            self.nav_frames = [self.nav_file_frame, self.nav_settings_frame, self.nav_help_frame]

            nav_file = createNavButton(self.nav_bar, width=50, height=NAVBAR_HEIGHT, text="File", font=consolas_regular15, command=lambda: self.showNavFrame(0))
            nav_controls = createNavButton(self.nav_bar, width=70, height=NAVBAR_HEIGHT, text="Controls", font=consolas_regular15, command=lambda: self.showNavFrame(1))
            nav_help = createNavButton(self.nav_bar, width=60, height=NAVBAR_HEIGHT, text="Help", font=consolas_regular15, command=lambda: self.showNavFrame(2))
            
            nav_file.place(x=0, y=0)
            nav_controls.place(x=50, y=0)
            nav_help.place(x=120, y=0)

            nav_file_save = NavSubButton(self.nav_file_frame, 120, 30, "Save config", consolas_regular15, self.saveConfig)
            nav_file_load = NavSubButton(self.nav_file_frame, 120, 30, "Load config", consolas_regular15, self.loadConfig)
            nav_file_loadpreset = NavSubButton(self.nav_file_frame, 120, 30, "Load preset", consolas_regular15, lambda: self.changeView(2))
            nav_settings_change = NavSubButton(self.nav_settings_frame, 120, 30, "Change settings", consolas_regular15, lambda: self.changeView(1))
            nav_settings_shtimer = NavSubButton(self.nav_settings_frame, 120, 30, "Show/Hide timer", consolas_regular15, self.toggleTimerWindow)
            nav_help_about = NavSubButton(self.nav_help_frame, 120, 30, "About", consolas_regular15, lambda: self.changeView(3))
            nav_help_git = NavSubButton(self.nav_help_frame, 120, 30, "My Github", consolas_regular15, self.openGithub)
            nav_help_htu = NavSubButton(self.nav_help_frame, 120, 30, "How to use", consolas_regular15, lambda: self.changeView(4))

            nav_file_save.place(x=0, y=0)
            nav_file_load.place(x=0, y=30)
            nav_file_loadpreset.place(x=0, y=60)
            nav_settings_change.place(x=0, y=0)
            nav_settings_shtimer.place(x=0, y=30)
            nav_help_about.place(x=0, y=0)
            nav_help_git.place(x=0, y=30)
            nav_help_htu.place(x=0, y=60)

            self.view_timers, self.view_settings, self.view_load_presets, self.view_about, self.view_htu = (
                ctk.CTkFrame(self, width=view_width, height=view_height, fg_color="#292929", corner_radius=6)
                for _ in range(5)
            )

            self.view_frames = [self.view_timers, self.view_settings, self.view_load_presets, self.view_about, self.view_htu]

            self.view_timers.place(relx=0.5, rely=0.5, anchor="center", y=12)

            # Load view content
            loadPreset_cb = ctk.CTkOptionMenu(self.view_load_presets, values=["FNaF 1", "FNaF 4", "SL Enard"], command=self.changePreset)
            loadPreset_btn = ctk.CTkButton(self.view_load_presets, text="Load", font=(self.CONSOLAS_REGULAR, 18), fg_color="#0bd972", hover_color="#0b8a4a", text_color="#000000", corner_radius=5, command=lambda: print(self.choosedPreset))

            loadPreset_cb.place(relx=0.5, rely=0.4, anchor="center")
            loadPreset_btn.place(relx=0.5, rely=0.6, anchor="center")

            createBackButton(self.view_load_presets, consolas_regular15, lambda: self.changeView(0))
            createBackButton(self.view_settings, consolas_regular15, lambda: self.changeView(0))
            createBackButton(self.view_about, consolas_regular15, lambda: self.changeView(0))
            createBackButton(self.view_htu, consolas_regular15, lambda: self.changeView(0))

            createTitle(self.view_load_presets, "Load Presets", consolas_regular24)
            createTitle(self.view_settings, "Settings", consolas_regular24)
            createTitle(self.view_htu, "How To Use", consolas_regular24)
            createTitle(self.view_timers, "Timers", consolas_regular24)
            createTitle(self.view_about, "About", consolas_regular24)

            




            return True

        except Exception as e:
            print(e)
            return False
        

    def loadInConfigData(self, data: dict) -> None:
        # logic
        
        ...
    

    def getConfigData(self) -> dict:
        data = {}

        # logic

        return data
        

def main() -> None:
    app = App()
    app.start()

if __name__ == "__main__":
    main()