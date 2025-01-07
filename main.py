from tkextrafont import Font as exFont

import customtkinter as ctk
import tkinter as tk

import os
os.system("cls")

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("assets/theme.json")


class TimerPreviev(ctk.CTkFrame):
    def __init__(self, master, color: str = "#ffffff") -> None:
        super().__init__(master, width=360, height=55, bg_color="#262626")

class App(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()
        self.DIMENTIONS = ( 400, 500 )

        self.geometry(f"{self.DIMENTIONS[0]}x{self.DIMENTIONS[1]}")
        self.iconbitmap("assets/images/favicon.ico")
        self.resizable(False, False)
        self.title("FNAF Interval Timer by VicExe")

        self.timerWindow = None
        self.currentScreen = 0

        if not self.loadFonts():
            print("Error: Failed to load fonts. Default fonts used instead")

        if not self.loadWidgets():
            print("Error: Failed to load widgets.")
            return


    def start(self) -> None:
        self.mainloop()


    def ACbutton_load(self) -> None:
        print("load")


    def ACbutton_save(self) -> None:
        print("save")


    def ACbutton_togglePreview(self) -> None:
        if self.timerWindow is None:
            self.button_togglePreview.configure(text="Hide Timer", fg_color="#bf1a11", hover_color="#82120c", text_color="#ffffff")
            # window creation logic

            self.timerWindow = "WINDOW OBJECT"

        else:
            self.button_togglePreview.configure(text="Show Timer", fg_color="#10ad3a", hover_color="#0c8a2e", text_color="#000000")
            # window destruction logic

            self.timerWindow = None



    def ACbutton_switchScreen(self, state: int) -> None:
        if self.currentScreen == state:
            return
        
        if state == 0:
            self.btn_timers.configure(fg_color="#212121", hover_color="#212121")
            self.frame_timers.place(x=10, y=40 + 10)

            self.btn_settings.configure(fg_color="#2e2e2e", hover_color="#262626")
            self.frame_settings.place_forget()

            self.currentScreen = 0


        elif state == 1:
            self.btn_settings.configure(fg_color="#212121", hover_color="#212121")
            self.frame_settings.place(x=10, y=40 + 10)

            self.btn_timers.configure(fg_color="#2e2e2e", hover_color="#262626")
            self.frame_timers.place_forget()

            self.currentScreen = 1


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


    def loadWidgets(self) -> bool:
        WIDTH, HEIGHT = self.DIMENTIONS

        h_WIDTH = WIDTH // 2
        h_HEIGHT = HEIGHT // 2

        try:
            self.btn_timers = ctk.CTkButton(self, text="Timers",
                                             width=h_WIDTH, 
                                             height=40, 
                                             font=(self.CONSOLAS_REGULAR, 20),
                                             corner_radius=0,
                                             fg_color="#212121", hover_color="#212121",
                                             command=lambda: self.ACbutton_switchScreen(0))
            
            self.btn_settings = ctk.CTkButton(self, text="Settings", 
                                             width=h_WIDTH, 
                                             height=40,
                                             font=(self.CONSOLAS_REGULAR, 20), 
                                             corner_radius=0, 
                                             fg_color="#2e2e2e", hover_color="#262626", 
                                             command=lambda: self.ACbutton_switchScreen(1))
            
            self.btn_timers.place(x=0, y=0)
            self.btn_settings.place(relx=1.0, y=0, anchor="ne")

            frame_width = WIDTH - 10 * 2
            frame_height = HEIGHT - 40 - 10 * 2

            self.frame_timers = ctk.CTkFrame(self, width=frame_width, height=frame_height, fg_color="#303030", corner_radius=5)
            self.frame_settings = ctk.CTkFrame(self, width=frame_width, height=frame_height, fg_color="#303030", corner_radius=5)

            self.frame_timers.place(x=10, y=40 + 10)

            self.button_save = ctk.CTkButton(self.frame_timers, text="Save", 
                                            width=150, height=30, 
                                            font=(self.CONSOLAS_REGULAR, 15),
                                            command=self.ACbutton_save)
            
            self.button_load = ctk.CTkButton(self.frame_timers, text="Load", 
                                            width=150, height=30, 
                                            font=(self.CONSOLAS_REGULAR, 15),
                                            command=self.ACbutton_load)

            self.button_save.place(x=25, y=15)
            self.button_load.place(relx=1.0, x=-25, y=15, anchor="ne")

            self.scroll_frame_timers = ctk.CTkScrollableFrame(self.frame_timers, width=frame_width-40, height=frame_height-105, bg_color="#1c1c1c")
            self.scroll_frame_timers.place(x=10, y=55)

            self.button_togglePreview = ctk.CTkButton(self.frame_timers, text="Show Timer", 
                                            width=150, height=30,
                                            fg_color="#10ad3a",
                                            hover_color="#0c8a2e",
                                            text_color="#000000",
                                            font=(self.CONSOLAS_REGULAR, 15),
                                            command=self.ACbutton_togglePreview)
            
            self.button_togglePreview.place(x=115, y=frame_height-40)



            
            return True

        except Exception as e:
            print(e)
            return False

def main() -> None:
    app = App()
    app.start()


if __name__ == "__main__":
    main()