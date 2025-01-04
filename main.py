from tkextrafont import Font as exFont
from tkinter import font as tkFont

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
        

    def loadWidgets(self) -> bool:
        try:
            self.button = ctk.CTkButton(self, text="Hello, World!", command=lambda: print("Clicked!"), font=(self.CONSOLAS_REGULAR, 17))
            self.button.pack(pady=20)

            return True

        except Exception as e:
            print(e)
            return False

def main() -> None:
    app = App()
    app.start()


if __name__ == "__main__":
    main()