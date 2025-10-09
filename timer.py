from __future__ import annotations
import pygame
from random import randint, random

class Timer:
    def __init__(self):
        """Simple timer with pause functionality"""
        self.total_time = 0
        self.pause_time = 0
        self.pause_duration = None
        self.on_hold = False

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
        if self.on_hold:
            if self.pause_duration is not None:
                self.pause_time += dt
                if self.pause_time >= self.pause_duration:
                    self.resume()
        else:
            self.total_time += dt

class ActionTimer(Timer):
    """Timer for cyclic actions and randomness"""
    def __init__(self, cycle_min: int | None = None, cycle_max: int | None = None):
        super().__init__()
        self.cycle_min = None
        self.cycle_max = None
        self.activated = False
        self.reset(cycle_min, cycle_max)

    def reset(self, cycle_min: int | None = None, cycle_max: int | None = None):
        super().reset()
        self.time_since_action = 0
        self.action_alarm = False
        self.cycle_min = cycle_min
        self.cycle_max = cycle_max 
        if self.cycle_min is None and self.cycle_max is None:
            self.activated = False
            self.cycle_time = None
        else:
            self.activated = True
        self._set_new_cycle_time()

    def _set_new_cycle_time(self):
        if not self.activated:
            self.cycle_time = None
        elif self.cycle_max is None:
            self.cycle_time = self.cycle_min
        elif self.cycle_min is None:
            self.cycle_time = self.cycle_max
        else:
            if self.cycle_min > self.cycle_max:
                self.cycle_min, self.cycle_max = self.cycle_max, self.cycle_min
            self.cycle_time = randint(self.cycle_min, self.cycle_max)

    def update(self, dt: int):
        super().update(dt)
        if self.activated and not self.on_hold:
            self.time_since_action += dt
            if self.time_since_action >= self.cycle_time:
                self.action_alarm = True
                self.time_since_action -= self.cycle_time
                self._set_new_cycle_time()
 
    def check_alarm(self) -> bool:
        """Return True (only once) when timer reaches its cycle time."""
        if self.action_alarm:
            self.action_alarm = False
            return True
        return False