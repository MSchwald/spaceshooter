import pygame, settings
from image import Image
from sprite import Sprite
from display import Display
from math import hypot as norm


class Item(Sprite):
    """A class to manage the items"""

    def __init__(self, type, level, grid=None, center=None, x=0, y=0, direction=(0,1), v=settings.item_speed):
        super().__init__(Image.load(f'images/item/{str(type)}.png'), grid=grid, center=center, x=x, y=y, v=v, direction=direction,
                         constraints=pygame.Rect([0, 0, Display.screen_width, Display.screen_height]), boundary_behaviour="vanish")
        self.type = type
        self.level = level

    def update(self, dt):
        if self.level.ship.magnet:
            temp = [self.level.ship.rect.center[i]-self.rect.center[i] for i in [0,1]]
            norm_temp = norm(temp[0],temp[1])
            if norm_temp!=0:
                temp = [settings.item_speed*temp[i]/norm_temp/30 for i in [0,1]]
            self.change_direction(self.vx+temp[0],self.vy)
            self.v = norm(self.direction[0],self.direction[1])
        super().update(dt)