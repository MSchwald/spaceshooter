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
    def __init__(self, cycle_min: int | None = None,
                        cycle_max: int | None = None):
        super().__init__()
        self.cycle_min = None
        self.cycle_max = None
        self.set_cyclic_alarm(cycle_min, cycle_max)

    def set_cyclic_alarm(self, cycle_min: int | None = None,
                                cycle_max: int | None = None):
        self.reset()
        self.cycle_min = cycle_min
        self.cycle_max = cycle_max 
        if self.cycle_min is None and self.cycle_max is None:
            self.pause()
            self.alarm_time = None
            return
        self.alarm_time = self._get_new_alarm_time()

    def _get_new_alarm_time(self) -> int:
        if self.cycle_max is None:
            self.on_hold = self.cycle_min is None
            return self.cycle_min
        if self.cycle_min is None:
            return self.cycle_max
        if self.cycle_min > self.cycle_max:
            self.cycle_min, self.cycle_max = self.cycle_max, self.cycle_min
        return randint(self.cycle_min, self.cycle_max)        
 
    def check_alarm(self) -> bool:
        """Return True (only once) when timer reaches its alarm time."""
        if self.on_hold:
            return False
        if self.total_time >= self.alarm_time:
            self.reset()
            self.alarm_time = self._get_new_alarm_time()
            return True

    @property
    def remaining_time(self) -> int:
        return self.alarm_time - self.total_time

