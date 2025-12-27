from __future__ import annotations
import pygame
from random import randint, random

class Timer:
    """Simple timer with pause functionality. Measures time in ms."""

    def __init__(self):
        self.reset()

    def reset(self):
        self.total_time = 0
        self.pause_time = 0
        self.pause_duration = None
        self.on_hold = False

    def pause(self, duration: int | None = None):
        """Pause timer for a specific duration or indefinitely"""
        self.on_hold = True
        self.pause_time = 0
        self.pause_duration = duration

    def resume(self):
        """Resume measuring time immediately"""
        self.on_hold = False
        self.pause_time = 0
        self.pause_duration = None

    def update(self, dt: int):
        """Updates measured time if timer is paused"""
        if not self.on_hold:
            self.total_time += dt
            return
        self.pause_time += dt
        if self.pause_duration is None:
            return
        if self.pause_time >= self.pause_duration:
            self.resume()
            

class ActionTimer(Timer):
    """Timer for single or cyclic actions and animation. Alarm can be randomized."""
    
    def __init__(self, alarm_min: int | None = None,
                        alarm_max: int | None = None,
                        cyclic: bool = True):
        """Set an alarm of a given time (if one number is provided)
        or randomly within a given range (if both numbers are provided).
        If cyclic is True, a new random alarm time gets chosen automatically."""
        super().__init__()
        self.set_alarm(alarm_min, alarm_max, cyclic)

    def set_alarm(self, alarm_min: int | None = None,
                        alarm_max: int | None = None,
                        cyclic: bool = True):
        """Change the alarm settings of the timer"""
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
        """Return True (only once) when timer reaches its alarm time.
        Set a new alarm automatically if cyclic = True was provided."""
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
        """Time that is left until the alarm gets triggered. Can't be negative."""
        return max(self.alarm_time - self.total_time, 0)