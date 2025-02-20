from timerscrollableframe import TimerScrollableFrame
from timer import TimerView, validateConfigDict
from typing import Optional, Callable, Any
from tkextrafont import Font as exFont
from colorpicker import ColorEntry
from bindbutton import BindButton
from tkinter import filedialog

import customtkinter as ctk
import webbrowser
import keyboard
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
        self.hotkey_ids = []

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
        
    def openGithub(self) -> None:
        self.closeNavBarFrame()
        webbrowser.open(GITHUB_URL)
        
    def showNavFrame(self, id: int) -> None: 
        for frame in self.nav_frames:
            frame.forgetFrame()

        pos = {
            0: 0,
            1: 50,
            2: 120,
            3: 180
        }.get(id, 0)

        frame = self.nav_frames[id]
        frame.placeFrame(x=pos, y=24)
        self.currentNavFrame = frame

    def saveConfigFile(self) -> None: 
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
            print("Failed to save config file.")
            return

    def loadConfigFile(self) -> None:
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

    def changeView(self, id: int) -> None:
        for view in self.view_frames:
            view.place_forget()

        self.bind_startstop.reset()
        self.bind_reset.reset()

        self.view_frames[id].place(relx=0.5, rely=0.5, anchor="center", y=12)
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
            self.hotkey_ids = []
            return
        
        data = self.getConfigData()
        self.timerWindow = TimerView(self, font=self.LCD_SOLID, config_data=data)

        self.timerWindow.createWindow()
        self.hotkey_ids = self.timerWindow.hotkey_ids

    def changePreset(self, choose) -> None:
        self.choosedPreset = choose

    def loadWidgets(self) -> bool:
        WIDTH, HEIGHT = self.WIDTH, self.HEIGHT

        try:
            NAVBAR_HEIGHT = 24
            view_height = HEIGHT-NAVBAR_HEIGHT-20
            view_width = WIDTH-20
            consolas_regular15 = (self.CONSOLAS_REGULAR, 15)
            consolas_regular20 = (self.CONSOLAS_REGULAR, 20)
            consolas_regular24 = (self.CONSOLAS_REGULAR, 24)
            consolas_regular30 = (self.CONSOLAS_REGULAR, 30)

            self.nav_bar = ctk.CTkFrame(self, width=WIDTH, height=NAVBAR_HEIGHT, fg_color="#292929")
            self.nav_version_label = ctk.CTkLabel(self.nav_bar, text=VERSION, font=(self.CONSOLAS_REGULAR, 14), text_color="#595959")

            self.nav_bar.place(x=0, y=0)
            self.nav_version_label.place(relx=1.0, rely=0.5, anchor="e", x=-5)

            self.nav_file_frame = NavFrame(self, width=120, height=60, fg_color="#363636")
            self.nav_settings_frame = NavFrame(self, width=120, height=60, fg_color="#363636")
            self.nav_help_frame = NavFrame(self, width=120, height=60, fg_color="#363636")
            
            self.nav_frames = [self.nav_file_frame, self.nav_settings_frame, self.nav_help_frame]

            nav_file = createNavButton(self.nav_bar, width=50, height=NAVBAR_HEIGHT, text="File", font=consolas_regular15, command=lambda: self.showNavFrame(0))
            nav_controls = createNavButton(self.nav_bar, width=70, height=NAVBAR_HEIGHT, text="Controls", font=consolas_regular15, command=lambda: self.showNavFrame(1))
            nav_help = createNavButton(self.nav_bar, width=60, height=NAVBAR_HEIGHT, text="Help", font=consolas_regular15, command=lambda: self.showNavFrame(2))
            
            nav_file.place(x=0, y=0)
            nav_controls.place(x=50, y=0)
            nav_help.place(x=120, y=0)

            nav_file_save = NavSubButton(self.nav_file_frame, 120, 30, "Save config", consolas_regular15, self.saveConfigFile)
            nav_file_load = NavSubButton(self.nav_file_frame, 120, 30, "Load config", consolas_regular15, self.loadConfigFile)
            nav_settings_change = NavSubButton(self.nav_settings_frame, 120, 30, "Settings", consolas_regular15, lambda: self.changeView(1))
            nav_settings_shtimer = NavSubButton(self.nav_settings_frame, 120, 30, "Show/Hide timer", consolas_regular15, self.toggleTimerWindow)
            nav_help_about = NavSubButton(self.nav_help_frame, 120, 30, "About", consolas_regular15, lambda: self.changeView(2))
            nav_help_git = NavSubButton(self.nav_help_frame, 120, 30, "My Github", consolas_regular15, self.openGithub)

            nav_file_save.place(x=0, y=0)
            nav_file_load.place(x=0, y=30)
            nav_settings_change.place(x=0, y=0)
            nav_settings_shtimer.place(x=0, y=30)
            nav_help_about.place(x=0, y=0)
            nav_help_git.place(x=0, y=30)

            self.view_timers, self.view_settings, self.view_about = (
                ctk.CTkFrame(self, width=view_width, height=view_height, fg_color="#292929", corner_radius=6)
                for _ in range(3)
            )

            self.view_frames = [self.view_timers, self.view_settings, self.view_about]

            self.view_timers.place(relx=0.5, rely=0.5, anchor="center", y=12)

            createBackButton(self.view_settings, consolas_regular15, lambda: self.changeView(0))
            createBackButton(self.view_about, consolas_regular15, lambda: self.changeView(0))

            createTitle(self.view_settings, "Settings", consolas_regular30)
            createTitle(self.view_timers, "Timers", consolas_regular30)
            createTitle(self.view_about, "About", consolas_regular30)

            binds_label = ctk.CTkLabel(self.view_settings, text="Binds", font=consolas_regular24)
            binds_label.place(x=20, y=40)

            startstop_label = ctk.CTkLabel(self.view_settings, text="start/stop", text_color="#d1d1d1", font=consolas_regular20)
            self.bind_startstop = BindButton(self.view_settings, default_button="`", width=150, height=20, font=consolas_regular20, fg_color="#424242", hover_color="#303030")
            
            startstop_label.place(x=20, y=70)
            self.bind_startstop.place(x=130, y=70)

            startstop_label = ctk.CTkLabel(self.view_settings, text="restart", text_color="#d1d1d1", font=consolas_regular20)
            self.bind_reset = BindButton(self.view_settings, default_button="=", width=150, height=20, font=consolas_regular20, fg_color="#424242", hover_color="#303030")

            startstop_label.place(x=20, y=100)
            self.bind_reset.place(x=130, y=100)

            window_label = ctk.CTkLabel(self.view_settings, text="Window", font=consolas_regular24)
            window_label.place(x=20, y=150)

            bgcolor_label = ctk.CTkLabel(self.view_settings, text="background color", text_color="#d1d1d1", font=consolas_regular24)
            self.bg_color_entry = ColorEntry(self.view_settings, height=20, width=120, font=consolas_regular20, default_color="#000000")

            bgcolor_label.place(x=20, y=180)
            self.bg_color_entry.place(x=220, y=180)

            aot_label = ctk.CTkLabel(self.view_settings, text="always on top", text_color="#d1d1d1", font=consolas_regular24)
            self.aot_checkbox = ctk.CTkCheckBox(self.view_settings, width=20, height=20, text="", onvalue=True, offvalue=False)
            
            aot_label.place(x=20, y=210)
            self.aot_checkbox.place(x=190, y=212, anchor="nw")
            self.aot_checkbox.select()

            gh_label = ctk.CTkLabel(self.view_settings, text="global hotkeys", text_color="#d1d1d1", font=consolas_regular24)
            self.gh_checkbox = ctk.CTkCheckBox(self.view_settings, width=20, height=20, text="", onvalue=True, offvalue=False)
            
            gh_label.place(x=20, y=240)
            self.gh_checkbox.place(x=190, y=242, anchor="nw")
            self.gh_checkbox.select()

            about_label = ctk.CTkLabel(self.view_about, font=(self.CONSOLAS_REGULAR, 18), wraplength=WIDTH-60, anchor="w", justify="left", 
                                       text="The FNaF Interval Timer is a specialized tool designed for players tackling challenges in Five Nights at Freddy's that require precise management of animatronic movement opportunities.\n\
                                        \rWhether you're aiming for power efficiency in the \"Greenrun\" challenge or optimizing your night strategy, this timer helps you track the exact moments animatronics can move.")
            about_label.place(relx=0.5, rely=0.43, anchor="center")

            self.timer_scroll_Frame = TimerScrollableFrame(self.view_timers, WIDTH-80, HEIGHT-100, consolas_regular24)
            self.timer_scroll_Frame.place(relx=0.5, rely=0.5, anchor="center", y=15)

            return True

        except Exception as e:
            print(e)
            return False

    def loadInConfigData(self, data: dict) -> None:
        window_settings = data["window_settings"]
        binds = data["binds"]
        global_timer = data["global_timer"]
        timers = data["timers"]

        self.bg_color_entry.setColor((0, window_settings["bg_color"]))

        if window_settings["always_on_top"]:
            self.aot_checkbox.select()
        else:
            self.aot_checkbox.deselect()

        if window_settings["global_hotkeys"]:
            self.gh_checkbox.select()
        else:
            self.gh_checkbox.deselect()

        self.bind_startstop.setKey(binds["startstop"])
        self.bind_reset.setKey(binds["restart"])
        
        self.timer_scroll_Frame.setGlobalTimer(global_timer)
        self.timer_scroll_Frame.setTimers(timers)

    def getConfigData(self) -> dict:
        global_timer_data = self.timer_scroll_Frame.getGlobalTimerData()

        data = {
            "window_settings": {
                "bg_color": self.bg_color_entry.getColor()[1],
                "always_on_top": bool(self.aot_checkbox.get()),
                "global_hotkeys": bool(self.gh_checkbox.get())
            },
            "binds": {
                "startstop": self.bind_startstop.getKey(),
                "restart": self.bind_reset.getKey() 
            },
            "global_timer": {
                "color": global_timer_data["color"],
                "frames": global_timer_data["frames"]
            },
            "timers": self.timer_scroll_Frame.getTimersData()
        }

        return data
        

def main() -> None:
    app = App()
    app.start()
    
    if not app.hotkey_ids is None and not len(app.hotkey_ids) == 0:
        for hotkey_id in app.hotkey_ids:

            if hotkey_id is None: 
                continue

            keyboard.remove_hotkey(hotkey_id)

        app.hotkey_ids = []

    app = None

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(e)