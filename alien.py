import pygame
from pygame.locals import *
import settings
import image
from sprite import Sprite


class Alien(Sprite):
    """A class to manage the enemies"""

    def __init__(self, type, grid=None, center=None, x=0, y=0, direction=[0,0]):
        super().__init__(image.alien[type], grid=grid, center=center, x=x, y=y, v=settings.type_speed[type], direction=direction,
                         constraints=pygame.Rect(settings.alien_constraints), boundary_behaviour="reflect")
        self.type = type
        self.energy = settings.type_energy[type]
        self.points = settings.type_points[type]

    def get_damage(self, damage):
        self.energy -= damage
