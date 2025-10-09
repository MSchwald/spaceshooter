from __future__ import annotations
import pygame
from random import randint, random

class Timer:
    def __init__(self):
        """Simple timer in ms with pause functionality"""
        self.reset()

    def reset(self):
        self.total_time = 0
        self.pause_time = 0
        self.pause_duration = None
        self.on_hold = False

    def pause(self, duration: int | None = None):
        """Pause for a specific duration or indefinitely"""
        self.on_hold = True
        self.pause_time = 0
        self.pause_duration = duration

    def resume(self):
        """Resume immediately"""
        self.on_hold = False
        self.pause_time = 0
        self.pause_duration = None

    def update(self, dt: int):
        if not self.on_hold:
            self.total_time += dt
            return
        self.pause_time += dt
        if self.pause_duration is None:
            return
        if self.pause_time >= self.pause_duration:
            self.resume()
            

class ActionTimer(Timer):
    """Timer for cyclic actions, animation and randomness"""
    def __init__(self, alarm_min: int | None = None,
                        alarm_max: int | None = None,
                        cyclic: bool = True):
        super().__init__()
        self.set_alarm(alarm_min, alarm_max, cyclic)

    def set_alarm(self, alarm_min: int | None = None,
                        alarm_max: int | None = None,
                        cyclic: bool = True):
        self.reset()
        self.alarm_min = alarm_min
        self.alarm_max = alarm_max
        self.cyclic = cyclic 
        self.alarm_time = self._get_new_alarm_time()

    def _get_new_alarm_time(self) -> int:
        if self.alarm_min is None and self.alarm_max is None:
            self.pause()
            return 0
        if self.alarm_max is None:
            return self.alarm_min
        if self.alarm_min is None:
            return self.alarm_max
        if self.alarm_min > self.alarm_max:
            self.alarm_min, self.alarm_max = self.alarm_max, self.alarm_min
        return randint(self.alarm_min, self.alarm_max)        
 
    def check_alarm(self) -> bool:
        """Return True (only once) when timer reaches its alarm time."""
        if self.on_hold:
            return False
        if self.total_time < self.alarm_time:
            return False
        if self.cyclic:
            self.reset()
            self.alarm_time = self._get_new_alarm_time()
        else:
            self.pause()
        return True

    @property
    def remaining_time(self) -> int:
        return max(self.alarm_time - self.total_time, 0)

