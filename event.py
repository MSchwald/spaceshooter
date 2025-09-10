import pygame, settings
from random import randint

class Event:
    def __init__(self, type, level, cycle_time=None, random_cycle_time=None):
        self.type=type
        self.level=level
        self.cycle_time = cycle_time
        self.random_cycle_time = random_cycle_time
        if random_cycle_time:
            self.cycle_time = randint(random_cycle_time[0],random_cycle_time[1])
        if self.cycle_time:
            self.action_timer = 0
        self.timer_on_hold = False

    def update(self,dt):
        if self.cycle_time and not self.timer_on_hold:
                self.action_timer += dt
                if self.action_timer >= self.cycle_time:
                    self.action_timer -= self.cycle_time
                    if self.random_cycle_time:
                        self.cycle_time = randint(self.random_cycle_time[0],self.random_cycle_time[1])
                    self.do_action()

    def do_action(self):
        if self.type == "asteroid_hail":
            self.level.alien_random_entrance("big_asteroid")