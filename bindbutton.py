from typing import Callable, Optional, Any

import customtkinter as ctk

class BindButton(ctk.CTkButton):
    def __init__(self, parent, default_button: str = "`", **kwargs) -> None:
        super().__init__(parent, text=default_button.title(), command=self.startListening, **kwargs)
        self.allowed_keys = "`1234567890-=qwertyuiop[]\\asdfghjkl;'zxcvbnm,./"
        self.button = default_button
        self.islistening = False

    def startListening(self) -> None:
        self.islistening = True
        self.configure(text="Bind a key...")
        self.bind("<Key>", self.changeKey)
        self.focus_set()

    def changeKey(self, event) -> None:
        key_char = event.char

        self.islistening = False
        self.unbind("<Key>")
        self.master.focus_set()

        if not key_char in self.allowed_keys or key_char == "":
            self.configure(text=self.button)
            return

        self.configure(text=key_char)
        self.button = key_char

    def reset(self) -> None:
        self.islistening = False
        self.unbind("<Key>")
        self.master.focus_set()

        self.configure(text=self.button)

    def setKey(self, key_char) -> None:
        self.button = key_char

    def getKey(self) -> str:
        return self.button