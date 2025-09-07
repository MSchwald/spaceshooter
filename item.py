import pygame, settings
import settings
from image import Image
from sprite import Sprite


class Item(Sprite):
    """A class to manage the items"""

    def __init__(self, type, level, grid=None, center=None, x=0, y=0, direction=(0,1), v=settings.item_speed, scaling_width=settings.item_size):
        if type == "small_asteroid":
            scaling_width=50
        super().__init__(Image.load(f'images/item/{str(type)}.png', scaling_width=scaling_width), grid=grid, center=center, x=x, y=y, v=v, direction=direction,
                         constraints=pygame.Rect(settings.item_constraints), boundary_behaviour="vanish")
        self.type = type
        self.level = level

    def update(self, dt):
        if self.level.ship.magnet:
            self.direction = (4*(self.level.ship.rect.center[0]-self.rect.center[0])/settings.screen_width,self.direction[1])
        super().update(dt)