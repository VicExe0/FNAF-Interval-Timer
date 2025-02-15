from changescrollableframe import ChangeScrollableFrame
from typing import Optional, Callable, Any
from colorpicker import ColorEntry
from PIL import Image

import customtkinter as ctk

class GlobalTimerEditor(ctk.CTkToplevel):
    def __init__(self, parent, data: dict, font: tuple, callback: Callable) -> None:
        super().__init__(parent)

        self.data = data
        self.callback = callback

        self.geometry("300x150")
        self.title("Edit Global Timer")
        self.configure(fg_color="#292929")

        font20 = (font[0], 20)

        frames_label = ctk.CTkLabel(self, text="Frames", font=font20)
        self.frames_entry = ctk.CTkEntry(self, font=(font[0], 16))
        self.frames_entry.insert(0, str(data["frames"]))

        frames_label.place(x=20, y=20)
        self.frames_entry.place(x=90, y=20)

        color_label = ctk.CTkLabel(self, text="Color", font=font20)
        self.color_picker = ColorEntry(self, 30, 140, font20, data["color"])

        color_label.place(x=20, y=50)
        self.color_picker.place(x=90, y=50)


        self.cancel_button = ctk.CTkButton(self, text="Cancel", font=font, width=100, corner_radius=5, fg_color="#cf0c43", hover_color="#780e2c", command=self.cancel)
        self.apply_button = ctk.CTkButton(self, text="Apply", font=font, width=100, corner_radius=5, fg_color="#0ce87a", hover_color="#0ea158", text_color="#000000", command=self.submit)

        self.cancel_button.place(rely=0.9, relx=0.5, anchor="e", x=-10, y=-10)
        self.apply_button.place(rely=0.9, relx=0.5, anchor="w", x=10, y=-10)

    def submit(self) -> None:
        frames = self.data["frames"]
        frames_entry_val = self.frames_entry.get()

        if frames_entry_val.isdigit():
            frames = int(frames_entry_val)

        data = {
            "color": self.color_picker.getColor()[1],
            "frames": frames
        }

        self.callback(data)
        self.destroy()

    def cancel(self) -> None:
        self.destroy()

class Editor(ctk.CTkToplevel):
    def __init__(self, parent, data: dict, callback, font: tuple) -> None:
        super().__init__(parent)

        self.data = data
        self.callback = callback

        title = self.data["title"]

        self.title(title)
        self.geometry("350x400")
        self.configure(fg_color="#292929")
        self.resizable(False, False)

        self.title_label = ctk.CTkLabel(self, text="Title", font=(font[0], 20))
        self.title_entry = ctk.CTkEntry(self, width=100, height=30, font=(font[0], 15))

        self.title_entry.insert(0, title)

        self.title_label.place(x=20, y=20)
        self.title_entry.place(x=65, y=20)

        self.color_label = ctk.CTkLabel(self, text="Color", font=(font[0], 20))
        self.color_entry = ColorEntry(self, height=25, width=140, font=font, default_color="#ffffff")

        self.color_entry.setColor([0, self.data["color"]])

        self.color_label.place(x=20, y=60)
        self.color_entry.place(x=75, y=60)

        self.default_frames_label = ctk.CTkLabel(self, text="Default frames", font=(font[0], 20))
        self.default_frames_entry = ctk.CTkEntry(self, width=100, height=30, font=(font[0], 15))

        self.default_frames_entry.insert(0, str(self.data["frames"]))

        self.default_frames_label.place(x=20, y=100)
        self.default_frames_entry.place(x=155, y=100)

        self.changes_scrollable_frame = ChangeScrollableFrame(self, self.data["changes"], 300, 100, font)
        self.changes_scrollable_frame.place(relx=0.5, y=135, anchor="n")
        
        self.cancel_button = ctk.CTkButton(self, text="Cancel", font=font, corner_radius=5, fg_color="#cf0c43", hover_color="#780e2c", command=self.cancel)
        self.apply_button = ctk.CTkButton(self, text="Apply", font=font, corner_radius=5, fg_color="#0ce87a", hover_color="#0ea158", text_color="#000000", command=self.submit)

        self.cancel_button.place(rely=0.9, relx=0.5, anchor="e", x=-10)
        self.apply_button.place(rely=0.9, relx=0.5, anchor="w", x=10)

    def submit(self) -> None:
        frames = self.data["frames"]
        frames_entry_val = self.default_frames_entry.get()

        if frames_entry_val.isdigit():
            frames = int(frames_entry_val)

        data = {
            "title": self.title_entry.get(),
            "color": self.color_entry.getColor()[1],
            "frames": frames,
            "visible": self.data["visible"],
            "changes": self.changes_scrollable_frame.getChanges()
        }

        self.callback(data)
        self.destroy()

    def cancel(self) -> None:
        self.destroy()


class TimerBlock(ctk.CTkFrame):
    def __init__(self, parent, font: tuple, id: int, remove_func: Callable, width: int, height: int) -> None:
        super().__init__(parent, width=width, height=height, fg_color="#404040")

        self.id = id
        self.font = font
        self.remove_func = remove_func
        self.editor_obj = None
        self.data = {
            "title": "Timer",
            "color": "#ffffff",
            "frames": 1024,
            "visible": True,
            "changes": []
        }

        gear_image = ctk.CTkImage(light_image=Image.open("assets/images/gear.png"), size=(30, 30))
        X_image = ctk.CTkImage(light_image=Image.open("assets/images/X.png"), size=(30, 30))

        self.visible_checkbox = ctk.CTkCheckBox(self, width=20, height=20, text="", border_color="#292929", onvalue=True, offvalue=False, command=self.updateVisibility)
        self.visible_checkbox.place(x=10, rely=0.5, anchor="w")
        self.visible_checkbox.select()

        remove_button = ctk.CTkButton(self, text="", image=X_image, width=30, height=30, fg_color="#3b3b3b", hover_color="#262626", corner_radius=5, command=self.remove)
        remove_button.place(x=40, rely=0.5, anchor="w")

        remove_button = ctk.CTkButton(self, text="", image=gear_image, width=30, height=30, fg_color="#3b3b3b", hover_color="#262626", corner_radius=5, command=self.editTimer)
        remove_button.place(x=90, rely=0.5, anchor="w")

        self.title_label = ctk.CTkLabel(self, text="Timer", font=font, text_color="#ffffff")
        self.title_label.place(x=150, rely=0.5, anchor="w")

    def updateVisibility(self) -> None:
        self.data["visible"] = self.visible_checkbox.get()

    def remove(self) -> None:
        self.remove_func(self.id)
        self.pack_forget()
        self.destroy()

    def getData(self) -> dict:
        return self.data

    def editTimer(self) -> None:
        if not self.editor_obj is None:
            self.editor_obj.cancel()
            self.editor_obj = None

        def callback(data):
            self.data = data
            self.title_label.configure(text=data["title"], text_color=data["color"])

        self.editor_obj = Editor(self, self.data, callback, self.font)

    def setData(self, data: dict) -> None:
        self.data = data

        self.title_label.configure(text=data["title"], text_color=data["color"])

        if data["visible"]:
            self.visible_checkbox.select()
        else:
            self.visible_checkbox.deselect()


class TimerScrollableFrame(ctk.CTkScrollableFrame):
    def __init__(self, parent, width: int, height: int, font: tuple) -> None:
        super().__init__(parent, width=width, height=height)

        self.font = font
        self.width = width
        self.height = height
        self.global_timer_window = None
        self.global_timer_data = {
            "color": "#ffffff",
            "frames": 3000
        }

        self.timers = []

        half = ( width - 20 ) // 2

        self.frame = ctk.CTkFrame(self, width=width, height=50)
        self.frame.pack(pady=5)

        self.add_timer1 = ctk.CTkButton(self.frame, width=half, height=50, text="Add Timer", font=self.font, fg_color="#1ac779", hover_color="#138a54", text_color="#000000", corner_radius=5, command=self.addTimer)
        self.gt_settings = ctk.CTkButton(self.frame, width=half, height=50, text="Global Timer", font=self.font, fg_color="#404040", hover_color="#2b2b2b", corner_radius=5, command=self.editGlobalTimer)

        self.add_timer1.pack(side="left", padx=5)
        self.gt_settings.pack(side="left", padx=5)

    def editGlobalTimer(self) -> None:
        if not self.global_timer_window is None:
            self.global_timer_window.cancel()
            self.global_timer_window = None

        def callback(data: dict) -> None:
            self.global_timer_data = data
            self.global_timer_window = None

        self.global_timer_window = GlobalTimerEditor(self, self.global_timer_data, self.font, callback)

    def addTimer(self) -> None:
        timer = TimerBlock(self, self.font, len(self.timers), self.removeTimer, self.width-10, 50)

        timer.pack(pady=5)

        self.timers.append(timer)

    def removeTimer(self, id: int) -> None:
        self.timers.pop(id)

        for index, timer in enumerate(self.timers):
            timer.id = index

    def setTimers(self, data: list[dict]) -> None:
        for item in self.timers:
            item.pack_forget()

        self.timers = []

        for index, item in enumerate(data):
            timer = TimerBlock(self, self.font, index, self.removeTimer, self.width-10, 50)

            timer.setData(item)

            timer.pack(pady=5)

            self.timers.append(timer)

    def getTimersData(self) -> list[dict]:
        data = []

        for timer in self.timers:
            n = timer.getData()

            data.append(n)

        return data

    def setGlobalTimer(self, data: dict) -> None:
        self.global_timer_data = data

    def getGlobalTimerData(self) -> dict:
        return self.global_timer_data