from tkextrafont import Font as exFont

import customtkinter as ctk
import tkinter as tk

import os
os.system("cls")

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("theme.json")

class App(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()
        self.DIMENTIONS = ( 400, 500 )

        self.geometry(f"{self.DIMENTIONS[0]}x{self.DIMENTIONS[1]}")
        self.iconbitmap("images/favicon.ico")
        self.resizable(False, False)
        self.title("FNAF Interval Timer by VicExe")

        self.timerWindow = None
        self.currentScreen = 0

        if not self.loadFonts():
            print("Error: Could not load fonts. Default fonts used instead")

        if not self.loadWidgets():
            print("Error: Could not load widgets.")
            return


    def start(self) -> None:
        self.mainloop()


    def loadFonts(self) -> bool:
        try:
            self.LCD_SOLID = "LCD Solid"
            self.CONSOLAS_REGULAR = "Consolas Regular"

            exFont(file="fonts/LcdSolid-VPzB.ttf", family=self.LCD_SOLID)
            exFont(file="fonts/Consolas-Regular.ttf", family=self.CONSOLAS_REGULAR)

            return True
        
        except Exception as e:
            self.LCD_SOLID = "Helvetica"
            self.CONSOLAS_REGULAR = "Helvetica"

            return False


    def switchScreen(self, state: int) -> None:
        if self.currentScreen == state:
            return
        
        if state == 0:
            self.btn_timers.configure(fg_color="#1f1f1f")
            self.btn_settings.configure(fg_color="#2e2e2e")

            self.frame_timers.place(x=0, y=40)
            self.frame_settings.place_forget()

            self.currentScreen = 0


        elif state == 1:
            self.btn_timers.configure(fg_color="#2e2e2e")
            self.btn_settings.configure(fg_color="#1f1f1f")

            self.frame_settings.place(x=0, y=40)
            self.frame_timers.place_forget()

            self.currentScreen = 1


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
                                             fg_color="#1f1f1f", hover_color="#1f1f1f",
                                             command=lambda: self.switchScreen(0))
            
            self.btn_settings = ctk.CTkButton(self, text="Settings", 
                                             width=h_WIDTH, height=40,
                                             font=(self.CONSOLAS_REGULAR, 20), 
                                             corner_radius=0, 
                                             fg_color="#2e2e2e", hover_color="#1f1f1f", 
                                             command=lambda: self.switchScreen(1))
            
            self.btn_timers.place(x=0, y=0)
            self.btn_settings.place(relx=1.0, y=0, anchor="ne")

            self.frame_timers = ctk.CTkFrame(self, width=WIDTH, height=HEIGHT-40, fg_color="transparent")
            self.frame_settings = ctk.CTkFrame(self, width=WIDTH, height=HEIGHT-40, fg_color="transparent")

            self.frame_timers.place(x=0, y=40)

            self.label1 = ctk.CTkLabel(self.frame_timers, text="Timers", font=(self.LCD_SOLID, 20))
            self.label2 = ctk.CTkLabel(self.frame_settings, text="Settings", font=(self.LCD_SOLID, 20))

            self.label1.pack(pady=20)
            self.label2.pack(pady=20)



            
            return True

        except Exception as e:
            print(e)
            return False

def main() -> None:
    app = App()
    app.start()


if __name__ == "__main__":
    main()