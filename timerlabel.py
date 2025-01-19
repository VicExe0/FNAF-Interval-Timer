from typing import Optional, Any
import customtkinter as ctk

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
