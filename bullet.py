import pygame
from pygame.locals import *
import settings
import image
from sprite import Sprite
from image import Image

class Bullet(Sprite):
    """A class to manage the bullets shot by the player or enemies"""

    def __init__(self, type, owner=None, damage=None, timer = None, image=None,
            v=None, grid=None, center=None, x=0, y=0, direction=None,
            constraints=pygame.Rect(0, 0, settings.screen_width, settings.screen_height),
            boundary_behaviour="vanish"):
        self.type = type
        if owner is None:
            owner = settings.bullet_owner[type]
        self.owner = owner
        if damage is None:
            damage = settings.bullet_damage[type]
        self.damage = damage
        if timer is None:
            timer = settings.bullet_timer[type]
        self.timer = timer
        if image is None:
            image = Image.load(f'images/bullet/{type}.png', scaling_width = settings.bullet_width[type])
        if v is None:
            v = settings.bullet_speed[type]
        if direction is None:
            if self.owner == "player":
                direction = (0,-1)
            else:
                direction = (0,1)
        super().__init__(image, grid=grid, center=center, x=x, y=y, v=v, direction=direction,
            constraints=constraints, boundary_behaviour=boundary_behaviour)

    def update(self, dt):
        super().update(dt)
        if self.timer:
            self.timer -= dt
            if self.timer <= 0:
                self.kill()