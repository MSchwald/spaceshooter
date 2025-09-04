import pygame
from pygame.locals import *
import settings
import image
from image import Image
from sprite import Sprite
from bullet import Bullet

class Alien(Sprite):
    """A class to manage the enemies"""

    def __init__(self, type, grid=None, center=None, x=0, y=0, direction=(0,0), scaling_width=settings.grid_width):
        super().__init__(Image.load(f'images/alien/{str(type)}.png',colorkey=settings.type_colorkey[type], scaling_width=settings.type_width[type]), grid=grid, center=center, x=x, y=y, v=settings.type_speed[type], direction=direction,
                         constraints=pygame.Rect(settings.alien_constraints), boundary_behaviour="reflect")
        self.type = type
        self.energy = settings.type_energy[type]
        self.points = settings.type_points[type]

    def get_damage(self, damage):
        self.energy -= damage

    def update(self, dt, level):
        if self.type == "purple":
            #purple aliens do actions every two seconds
            if self.timer//1000 !=(self.timer+dt)//1000:
                level.bullets.add(Bullet("g",center=self.rect.midbottom))

        #timer, movement and animation are handles in the Sprite class
        super().update(dt)
