from __future__ import annotations
import pygame
from random import randint, random
from settings import ALIEN

class Event:
    """Create and manage cyclic level events like repeated enemy spawns"""
    def __init__(self, template: str,
                level: Level,
                random_cycle_time: tuple[int, int] | None = None):
        self.template=template
        self.level=level
        self.random_cycle_time = random_cycle_time
        self.cycle_time = randint(random_cycle_time[0], random_cycle_time[1])
        self.action_timer = 0
        self.timer_on_hold = False

    def update(self,dt):
        if self.cycle_time and not self.timer_on_hold:
            self.action_timer += dt
            if self.action_timer >= self.cycle_time:
                self.action_timer -= self.cycle_time
                if self.random_cycle_time:
                    self.cycle_time = randint(self.random_cycle_time[0], self.random_cycle_time[1])
                self.do_action()

    def do_action(self):
        if self.template == "asteroid_hail":
            self.level.encounter(ALIEN.BIG_ASTEROID, boundary_behaviour = "vanish")
        if self.template == "alien_attack":
            if random() > 0.5:
                self.level.encounter(ALIEN.PURPLE)
            else:
                self.level.encounter(ALIEN.BLOB, energy = ALIEN.BLOB.energy//4)