from __future__ import annotations
import pygame
from random import randint, random
from settings import ALIEN
from timer import ActionTimer

class Event(ActionTimer):
    """Create and manage cyclic level events like repeated enemy spawns"""
    def __init__(self, template: str,
                level: Level,
                random_cycle_time: tuple[int, int]):
        self.template = template
        self.level = level
        super().__init__(random_cycle_time[0], random_cycle_time[1])

    def update(self,dt):
        if self.check_alarm():
            self.do_action()

    def do_action(self):
        if self.template == "asteroid_hail":
            self.level.encounter(ALIEN.BIG_ASTEROID, boundary_behaviour = "vanish")
        if self.template == "alien_attack":
            if random() > 0.5:
                self.level.encounter(ALIEN.PURPLE, boundary_behaviour = "reflect")
            else:
                self.level.encounter(ALIEN.BLOB, energy = ALIEN.BLOB.energy//4)
