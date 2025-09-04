import pygame
from pygame.locals import *
import settings
import image
from image import Image
from sprite import Sprite
from bullet import Bullet
from random import random,choice,randint

class Alien(Sprite):
    """A class to manage the enemies"""

    def __init__(self, type, cycle_time=None, random_cycle_time=(1000,2000),
                grid=None, center=None, x=0, y=0, direction=(0,0),
                scaling_width=settings.grid_width):
        #cycle_time: Alien macht periodische Aktionen (in ms)
        #random_cycle_time ein Tupel von Zahlen: Alien macht zufällige im vorgegebenen Zeitintervall Aktionen (in ms)
        super().__init__(Image.load(f'images/alien/{str(type)}.png',colorkey=settings.type_colorkey[type], scaling_width=settings.type_width[type]), grid=grid, center=center, x=x, y=y, v=settings.type_speed[type], direction=direction,
                         constraints=pygame.Rect(settings.alien_constraints), boundary_behaviour="reflect")
        self.type = type
        self.energy = settings.type_energy[type]
        self.points = settings.type_points[type]
        self.cycle_time = cycle_time
        self.random_cycle_time = random_cycle_time
        if random_cycle_time:
            self.cycle_time = randint(random_cycle_time[0],random_cycle_time[1])
        if self.cycle_time:
            self.action_timer = 0

    def get_damage(self, damage):
        self.energy -= damage

    def update(self, dt, level):
        if self.cycle_time and not self.timer_on_hold:
            self.action_timer += dt
            if self.action_timer >= self.cycle_time:
                self.action_timer -= self.cycle_time
                if self.random_cycle_time:
                    self.cycle_time = randint(self.random_cycle_time[0],self.random_cycle_time[1])
                if self.type == "purple":
                    #purple aliens shoot bullets
                    level.bullets.add(Bullet("g",center=self.rect.midbottom))

                elif self.type == "ufo":
                    #ufo aliens throw purple aliens
                    level.aliens.add(Alien("purple",center=self.rect.midbottom, direction=(2*random()-1,1)))

        #timer, movement and animation get handled in the Sprite class
        super().update(dt)
