from timerlabel import TimerLabel
from typing import Optional, Any
from threading import Thread

import customtkinter as ctk
import tkinter as tk
import keyboard
import time
import json
import re

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("assets/theme.json")

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


def readSettignsFile(path: str) -> Optional[dict]:
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
        
        if not existsWithInstance(ws, "default_font", str):
            print("Missing or invalid 'default_font' in 'window_settings'.")
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


class TimerView(ctk.CTkToplevel):
    def __init__(self, master, config_data: Optional[dict] = None, config_path: Optional[str] = None):
        self.master = master
        self.always_on_top = True
        self.running = False
        self.frame_length = 1 / 60
        self.hotkey_ids = []
        
        if not config_data is None:
            self.config = config_data

        elif not config_path is None:
            self.config = readSettignsFile(config_path)

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

        default_font = window_settings['default_font']

        main_timer_font_size = 45      # global timer font size
        regular_timer_font_size = 40   # rest of the timers font size

        g_timer_height = getTextHeight(default_font, main_timer_font_size)
        timer_height = getTextHeight(default_font, regular_timer_font_size)

        window_height = g_timer_height + timer_height * len(timers)

        self.geometry(f"200x{window_height}")
        self.configure(fg_color=window_settings['bg_color'])

        self._createTimerLabels(global_timer, timers, timer_height, default_font, [main_timer_font_size, regular_timer_font_size])

    def destroyWindow(self) -> None:
        if hasattr(self, "_drag_callbacks"):
            for event, callback in self._drag_callbacks.items():
                self.unbind(event)

        self.unbind_all("<Key>")

        for hotkey_id in self.hotkey_ids:
            keyboard.remove_hotkey(hotkey_id)
        self.hotkey_ids.clear()

        self.destroy()

    def pauseResumeTimers(self) -> None:
        self.running = not self.running

        if self.running:
            self.last_time = time.time()
            self.updateTimers()

    def resetTimers(self) -> None:
        self.running = False

        for timer in self.all_timers:
            timer.resetToInitial()
            timer.update(self.g_timer.remainingFrames)

    def updateTimers(self) -> None:
        if not self.running:
            return
        
        current_time = time.time()
        delta_time = current_time - self.last_time
        self.last_time = current_time
        
        for index, timer in enumerate(self.all_timers):
            timer.decrementFrames()

            if index == 0 and timer.remainingFrames <= 0:
                self.running = False

            timer.update(self.g_timer.remainingFrames)

        sleep_time = max(0, self.frame_length - delta_time)

        self.after(int(sleep_time * 1000), self.updateTimers)
 