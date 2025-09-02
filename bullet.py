import pygame
from pygame.locals import *
import settings
import image
from sprite import Sprite
from image import Image


Image.load('images/bullet/15.png', scaling_width = settings.missile_explosion_size)

class Bullet(Sprite):
    """A class to manage the bullets shot by the ship"""

    def __init__(self, x, y, speed, size, timer = None):
        self.timer = timer

        super().__init__(Image.load(f'images/bullet/{size}.png'), x=x, y=y, v=speed, direction=(0, -1), constraints=pygame.Rect(
            0, 0, settings.screen_width, settings.screen_height), boundary_behaviour="vanish")
        self.damage = size

    def update(self, dt):
        super().update(dt)
        if self.damage == 15:
            self.timer -= dt
            if self.timer <= 0:
                self.kill()