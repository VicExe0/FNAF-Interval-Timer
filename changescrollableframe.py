from typing import Optional, Callable, Any
from colorpicker import ColorEntry
from PIL import Image

import customtkinter as ctk

class ChangeBlock(ctk.CTkFrame):
    def __init__(self, parent, font: tuple, id: int, remove_func: Callable, width: int, height: int) -> None:
        super().__init__(parent, width=width, height=height, fg_color="#404040")

        self.id = id
        self.font = font
        self.remove_func = remove_func
        self.data = {
            "trigger_frame": 100,
            "change_to": 1000,
            "overwrite": False
        }

        font13 = (font[0], 13)

        X_image = ctk.CTkImage(light_image=Image.open("assets/images/X.png"), size=(30, 30))

        remove_button = ctk.CTkButton(self, text="", image=X_image, width=30, height=30, fg_color="#3b3b3b", hover_color="#262626", corner_radius=5, command=self.remove)
        remove_button.place(x=10, rely=0.5, anchor="w")

        overwrite_label = ctk.CTkLabel(self, text="Overwrite", font=font13)
        self.overwrite_checkbox = ctk.CTkCheckBox(self, width=15, height=15, text="", border_color="#1c1c1c", onvalue=True, offvalue=False)

        overwrite_label.place(x=90, y=10, anchor="center")
        self.overwrite_checkbox.place(rely=0.5, anchor="center", x=90, y=5)


        trigger_frame_label = ctk.CTkLabel(self, text="Target frame", font=font13)
        self.trigger_frame_entry = ctk.CTkEntry(self, width=50, height=15, font=font13)

        self.trigger_frame_entry.insert(0, str(self.data["trigger_frame"]))

        trigger_frame_label.place(x=165, y=10, anchor="center")
        self.trigger_frame_entry.place(rely=0.5, anchor="center", x=165, y=5)


        change_to_label = ctk.CTkLabel(self, text="Change to", font=font13)
        self.change_to_entry = ctk.CTkEntry(self, width=50, height=15, font=font13)

        self.change_to_entry.insert(0, str(self.data["change_to"]))

        change_to_label.place(x=240, y=10, anchor="center")
        self.change_to_entry.place(rely=0.5, anchor="center", x=240, y=5)

    def remove(self) -> None:
        self.remove_func(self.id)
        self.pack_forget()
        self.destroy()

    def getData(self) -> dict:
        trigger_frame = self.data["trigger_frame"]
        change_to = self.data["change_to"]

        trigger_frame_entry_val = self.trigger_frame_entry.get()
        change_to_entry_val = self.change_to_entry.get()

        if trigger_frame_entry_val.isdigit():
            trigger_frame = int(trigger_frame_entry_val)

        if change_to_entry_val.isdigit():
            change_to = int(change_to_entry_val)

        data = {
            "trigger_frame": trigger_frame,
            "change_to": change_to,
            "overwrite": self.overwrite_checkbox.get()
        }

        return data
    
    def setData(self, data: dict) -> None:
        self.data = data

        if data["overwrite"]:
            self.overwrite_checkbox.select()

        self.trigger_frame_entry.delete(0, 'end')
        self.change_to_entry.delete(0, 'end')

        self.trigger_frame_entry.insert(0, str(data["trigger_frame"]))
        self.change_to_entry.insert(0, str(data["change_to"]))


class ChangeScrollableFrame(ctk.CTkScrollableFrame):
    def __init__(self, parent, data: list[dict], width: int, height: int, font: tuple) -> None:
        super().__init__(parent, width=width, height=height)

        self.font = font
        self.data = data
        self.width = width
        self.height = height

        self.changes = []

        self.add_button = ctk.CTkButton(self, width=width-10, height=40, text="Add Change", font=self.font, fg_color="#1ac779", hover_color="#138a54", text_color="#000000", corner_radius=5, command=self.addChange)
        self.add_button.pack(pady=5, padx=5)

        self.setChanges(data)


    def addChange(self) -> None:
        change = ChangeBlock(self, self.font, len(self.changes), self.removeChange, self.width-10, 50)
        
        change.pack(pady=5)

        self.changes.append(change)

    def removeChange(self, id) -> None:
        self.changes.pop(id)

        for index, change in enumerate(self.changes):
            change.id = index

    def getChanges(self) -> list[dict]:
        data = []

        for item in self.changes:
            data.append(item.getData())

        return data
    
    def setChanges(self, data: list[dict]) -> None:
        for index, item in enumerate(data):
            change = ChangeBlock(self, self.font, index, self.removeChange, self.width-10, 50)

            change.setData(item)

            change.pack(pady=5)

            self.changes.append(change)