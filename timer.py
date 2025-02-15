from typing import Optional, Any
from threading import Thread

import customtkinter as ctk
import tkinter as tk
import keyboard
import time
import json
import re

def getTextHeight(font_family, font_size):
    root = tk.Tk()
    root.withdraw()

    canvas = tk.Canvas(root)
    font = (font_family, font_size)
    text_id = canvas.create_text(0, 0, text="A", font=font, anchor="nw")
    bbox = canvas.bbox(text_id)
    text_height = bbox[3] - bbox[1]

    root.destroy()
    return text_height


def readConfigFile(path: str) -> Optional[dict]:
    try:
        with open(path, "r") as f:
            data = json.load(f)

        return data
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Config file error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

    return None


def validateConfigDict(config) -> bool:
    MIN_FRAME_REQ = 0

    def isValidColor(hex_value: str) -> bool:
        return bool(re.fullmatch(r"#[0-9a-fA-F]{6}", hex_value))
    
    def existsWithInstance(data: dict, value: str, instance: type | tuple) -> bool:
        return value in data and isinstance(data[value], instance)
    
    def validateChanges(changes: list) -> bool:
        if not isinstance(changes, list):
            print("Invalid type of 'changes'.")
            return False
        
        for change in changes:
            if not existsWithInstance(change, "trigger_frame", int):
                print("Missing or invalid 'trigger_frame'.")
                return False
            
            if change["trigger_frame"] <= MIN_FRAME_REQ:
                print(f"'trigger_frame' has to be higher than {MIN_FRAME_REQ}")
                return False
            
            if not existsWithInstance(change, "change_to", int):
                print("Missing or invalid 'change_to'.")
                return False
            
            if change["change_to"] <= MIN_FRAME_REQ:
                print(f"'change_to' has to be higher than {MIN_FRAME_REQ}")
                return False
            
            if not existsWithInstance(change, "overwrite", bool):
                print("Missing or invalid 'overwrite'.")
                return False

        return True

    def validateTimers(timers: list) -> bool:
        if not isinstance(timers, list):
            print("Invalid type of 'timers'.")
            return False
        
        if len(timers) == 0:
            return True
        
        for timer in timers:
            if not existsWithInstance(timer, "color", str):
                print("Missing or invalid 'color' in timer.")
                return False
            
            if not isValidColor(timer["color"]):
                print("Invalid 'color'.")
                return False
            
            if not existsWithInstance(timer, "frames", int):
                print("Missing or invalid 'frames'.")
                return False
            
            if not existsWithInstance(timer, "title", str):
                print("Missing or invalid 'title'.")
                return False
            
            if not existsWithInstance(timer, "visible", bool):
                print("Missing or invalid 'visible'.")
                return False
            
            if timer["frames"] <= MIN_FRAME_REQ:
                print(f"'frames' has to be higher than {MIN_FRAME_REQ}")
                return False
            
            if not existsWithInstance(timer, "changes", list):
                print("Missing or invalid 'changes' in 'timers'")
                return False
            
            if len(timer["changes"]) > 0 and not validateChanges(timer["changes"]):
                print("Invalid changes")
                return False
            
            return True

    def validateWS(ws: dict) -> bool:
        if not existsWithInstance(ws, "bg_color", str):
            print("Missing or invalid 'bg_color' in 'window_settings'.")
            return False
        
        if not isValidColor(ws["bg_color"]):
            print("Invalid 'bg_color' in 'window_settings'.")
            return False
        
        if not existsWithInstance(ws, "always_on_top", bool):
            print("Missing or invalid 'always_on_top' in 'window_settings'.")
            return False
        
        if not existsWithInstance(ws, "global_hotkeys", bool):
            print("Missing or invalid 'global_hotkeys' in 'window_settings'.")
            return False
        
        return True
        

    def validateBinds(binds: dict) -> bool:
        if not existsWithInstance(binds, "startstop", str):
            print("Missing or invalid 'startstop' in 'binds'.")
            return False
        
        if not existsWithInstance(binds, "restart", str):
            print("Missing or invalid 'restart' in 'binds'.")
            return False
        
        return True

    def validateGT(gt: dict) -> bool:
        if not existsWithInstance(gt, "color", str):
            print("Missing or invalid 'color' in 'global_timer'.")
            return False
        
        if not isValidColor(gt["color"]):
            print("Invalid 'color' in 'global_timer'.")
            return False
        
        if not existsWithInstance(gt, "frames", int):
            print("Missing or invalid 'frames' in 'global_timer'.")
            return False
        
        if gt["frames"] <= MIN_FRAME_REQ:
            print(f"'frames' has to be higher than {MIN_FRAME_REQ}")
            return False
        
        return True


    FUNCTIONS = {
        "window_settings": validateWS,
        "binds": validateBinds,
        "global_timer": validateGT
    }

    for key in ["window_settings", "binds", "global_timer"]:
        if not existsWithInstance(config, key, dict):
            print(f"Missing or invalid '{key}'.")
            return False
        
        validateFunc = FUNCTIONS[key]

        if not validateFunc(config[key]):
            print(f"Invalid '{key}' structure.")
            return False
    
    if "timers" not in config or not isinstance(config["timers"], list):
        print("Missing or invalid 'timers'.")
        return False
    
    if not validateTimers(config["timers"]):
        print("Invalid 'timers' structure.")
        return False

    return True


class TimerLabel:
    def __init__(self, master, total_frames: int, padLength: int, color: str, font: tuple) -> None:
        self.label = ctk.CTkLabel(master, text=f"{total_frames:0>{padLength}}", text_color=color, font=font)
        self.maxFrames = total_frames
        self.remainingFrames = total_frames
        self.initialFrames = total_frames
        self.padLength = padLength
        self.isGlobal = False
        self.frameChanges = []
        self.numFrameChanges = 0
        self.master = master

    def _applyFrameChanges(self, globalFrames: int) -> None:
        for change in self.frameChanges:
            if change["done"] or globalFrames > change["trigger_frame"]:
                continue

            self.maxFrames = change["change_to"]

            if change["overwrite"]:
                self.reset()

            change["done"] = True

    def configureChanges(self, *changes: dict | list[dict]) -> None:
        if not changes:
            return

        if len(changes) == 1 and isinstance(changes[0], list):
            changeList = changes[0]
        else:
            changeList = changes

        for change in changeList:
            change["done"] = False
            self.frameChanges.append(change)

        self.numFrameChanges = len(self.frameChanges)

    def setGlobalState(self, state: bool = True) -> None:
        self.isGlobal = state

    def resetToInitial(self) -> None:
        self.remainingFrames = self.initialFrames
        self.maxFrames = self.initialFrames

        for change in self.frameChanges:
            change["done"] = False

    def decrementFrames(self) -> None:
        if self.remainingFrames > 0:
            self.remainingFrames -= 1

    def reset(self) -> None:
        self.remainingFrames = self.maxFrames

    def place(self, **kwargs) -> None:
        self.label.place(**kwargs)

    def update(self, globalFrames: int) -> None:
        if not self.isGlobal and self.numFrameChanges != 0:
            self._applyFrameChanges(globalFrames)

        if self.remainingFrames <= 0:
            self.reset()

        self.label.configure(text=f"{self.remainingFrames:0>{self.padLength}}")

    def __getattr__(self, value: Any) -> Optional[Any]:
        if value in self.__dict__:
            return self.__dict__[value]
        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{value}'")


class TimerView(ctk.CTkToplevel):
    def __init__(self, master, font: str, config_data: Optional[dict] = None, config_path: Optional[str] = None):
        self.master = master
        self.font = font
        self.always_on_top = True
        self.running = False
        self.frame_length = 1 / 60
        self.hotkey_ids = []
        self.TOLERANCE = 0.00285535499956796

        self.time_o = 0
        self.total = 0
        self.count = 0
        
        if not config_data is None:
            self.config = config_data

        elif not config_path is None:
            self.config = readConfigFile(config_path)

            if self.config is None:
                raise ValueError(f"Failed to load config from '{config_path}'.")
            
        else:
            raise ValueError("Config value is required")
        
        if not validateConfigDict(self.config):
            raise ValueError(f"Config data is corrupted or incorrect.")

    def _makeWindowDragable(self) -> bool:
        try:
            self.overrideredirect(True)

            def saveOffset(event):
                self._offsets = [event.x_root - self.winfo_x(), event.y_root - self.winfo_y()]

            def drag(event):
                if hasattr(self, "_offsets"):
                    x = event.x_root - self._offsets[0]
                    y = event.y_root - self._offsets[1]
                    self.geometry(f"+{x}+{y}")

            self.bind("<Button-1>", saveOffset)
            self.bind("<B1-Motion>", drag)

            self._drag_callbacks = {"<Button-1>": saveOffset, "<B1-Motion>": drag}

            return True
        except Exception as e:
            print(f"Error making window draggable: {e}")
            return False

        
    def _setupGlobalHotkeys(self, binds: dict):
        def listener():
            self.hotkey_ids.append(keyboard.add_hotkey(binds.get('startstop', 'ctrl+alt+s'), self.pauseResumeTimers))
            self.hotkey_ids.append(keyboard.add_hotkey(binds.get('restart', 'ctrl+alt+r'), self.resetTimers))
            keyboard.wait()

        Thread(target=listener, daemon=True).start()

    def _loadConfig(self) -> bool:
        try:
            window_settings = self.config.get('window_settings', {})
            if not window_settings:
                raise ValueError("Missing 'window_settings' in configuration.")

            binds = self.config.get('binds', {})
            if not binds:
                raise ValueError("Missing 'binds' in configuration.")

            self.attributes('-topmost', window_settings.get('always_on_top', False))

            if window_settings.get('global_hotkeys', False):
                self._setupGlobalHotkeys(binds)
            else:
                self.bind(binds.get('startstop', '<Control-s>'), self.pauseResumeTimers)
                self.bind(binds.get('restart', '<Control-r>'), self.resetTimers)

            self.resizable(False, False)

            return True
        except Exception as e:
            print(f"Error loading settings: {e}")
            return False
        
    def _createTimerLabels(self, global_timer: dict, timers: list[dict], height: int, font: str, font_sizes: list[int]) -> None:
        frames = global_timer['frames']
        paddingWidth = max(len(str(frames)), 4)

        self.g_timer = TimerLabel(self, frames, paddingWidth, global_timer['color'], (font, font_sizes[0]))
        self.g_timer.place(relx=0.5, y=23, anchor="center")
        self.g_timer.setGlobalState()
        
        self.all_timers = [self.g_timer]

        y_pos = 7
        for timer in timers:
            if not timer["visible"]:
                continue

            frames = timer["frames"]
            paddingWidth = max(len(str(frames)), 4)
            
            side_timer = TimerLabel(self, frames, paddingWidth, timer['color'], (font, font_sizes[1]))
            side_timer.configureChanges(timer['changes'])
            
            y_pos += height

            side_timer.place(x=5, y=y_pos)

            self.all_timers.append(side_timer)


    def createWindow(self) -> None:
        super().__init__(self.master)

        if not self._makeWindowDragable():
            print("Failed to make window dragable.")
            return

        if not self._loadConfig():
            print("Failed to load settings.")
            return

        window_settings, global_timer, timers = (
            self.config['window_settings'],
            self.config['global_timer'],
            self.config['timers'],
        )

        main_timer_font_size = 45      # global timer font size
        regular_timer_font_size = 40   # rest of the timers font size

        g_timer_height = getTextHeight(self.font, main_timer_font_size)
        timer_height = getTextHeight(self.font, regular_timer_font_size)

        timers_count = sum(1 for i in timers if i.get("visible", False))
        window_height = g_timer_height + timer_height * timers_count

        self.geometry(f"200x{window_height}")
        self.configure(fg_color=window_settings['bg_color'])

        self._createTimerLabels(global_timer, timers, timer_height, self.font, [main_timer_font_size, regular_timer_font_size])

    def destroyWindow(self) -> None:
        if hasattr(self, "_drag_callbacks"):
            for event, callback in self._drag_callbacks.items():
                self.unbind(event)

        self.unbind_all("<Key>")

        for hotkey_id in self.hotkey_ids:
            keyboard.remove_hotkey(hotkey_id)
        
        self.hotkey_ids = []

        self.destroy()

    def resetTimers(self, *args) -> None:
        self.running = False

        for timer in self.all_timers:
            timer.resetToInitial()
            timer.update(self.g_timer.remainingFrames)

    def pauseResumeTimers(self, *args) -> None:
        self.running = not self.running

        self.time_o = time.perf_counter()

        if self.running:
            self.total = 0
            self.last_time = time.perf_counter()
            self.updateTimers()

    def updateTimers(self) -> None:
        if not self.running:
            return
        
        start_time = time.perf_counter()

        for index, timer in enumerate(self.all_timers):
            timer.decrementFrames()

            if index == 0 and timer.remainingFrames <= 0:
                self.running = False

            timer.update(self.g_timer.remainingFrames)

        elapsed = time.perf_counter() - start_time
        delay = max(0, self.frame_length - elapsed - self.TOLERANCE)
        self.total += delay

        self.after(int(delay * 1000), self.updateTimers)