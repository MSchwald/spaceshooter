import pygame, settings
import settings
from image import Image
from sprite import Sprite


class Item(Sprite):
    """A class to manage the items"""

    def __init__(self, type, grid=None, center=None, x=0, y=0, direction=[0,1], v=settings.item_speed, scaling_width=settings.item_size):
        if type == "small_asteroid":
            scaling_width=50
        super().__init__(Image.load(f'images/item/{str(type)}.png', scaling_width=scaling_width), grid=grid, center=center, x=x, y=y, v=v, direction=direction,
                         constraints=pygame.Rect(settings.item_constraints), boundary_behaviour="vanish")
        self.type = type

    def update(self, dt, ship):
        if ship.magnet:
            self.direction[0]=4*(ship.rect.center[0]-self.rect.center[0])/settings.screen_width
        super().update(dt)