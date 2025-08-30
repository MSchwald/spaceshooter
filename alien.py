import pygame
from pygame.locals import *
import settings
import image
from sprite import Sprite


class Alien(Sprite):
    """A class to manage the enemies"""

    def __init__(self, x, y, type, direction):
        super().__init__(image.alien[type], x, y, v=settings.type_speed[type], direction=direction,
                         constraints=pygame.Rect(settings.alien_constraints), boundary_behaviour="reflect")
        self.type = type
        self.energy = settings.type_energy[type]
        self.points = settings.type_points[type]

    def get_damage(self, damage):
        self.energy -= damage
