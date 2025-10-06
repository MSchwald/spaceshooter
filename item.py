import pygame, settings
from image import Image
from sprite import Sprite
from display import Display
from math import hypot as norm
import sound

class Item(Sprite):
    """A class to manage the items"""

    def __init__(self, type, level, grid=None, center=None, x=0, y=0, direction=(0,1), v=settings.Item.SPEED):
        super().__init__(Image.load(f'images/item/{str(type)}.png'), grid=grid, center=center, x=x, y=y, v=v, direction=direction,
                         constraints=pygame.Rect([0, 0, Display.screen_width, Display.screen_height]), boundary_behaviour="vanish")
        self.type = type
        self.level = level
        self.effect_duration = settings.Item.EFFECT_DURATION[type]
        if self.effect_duration:
            self.effect_duration *= 1000

    def play_collecting_sound(self):
        match self.type:
            case "bullets_buff" | "magnet" | "score_buff" | "speed_buff":
                sound.item_collect.play()
            case "hp_plus" | "shield":
                sound.good_item.play()
            case "life_plus":
                sound.extra_life.play()
            case "missile":
                sound.collect_missile.play()
            case "ship_buff":
                sound.ship_level_up.play()
            case "size_plus":
                sound.grow.play()
            case "size_minus":
                sound.shrink.play()
            case "speed_nerf":
                sound.bad_item.play()

    def update(self, dt):
        if self.level.ship.magnet:
            temp = [self.level.ship.rect.center[i]-self.rect.center[i] for i in [0,1]]
            norm_temp = norm(temp[0],temp[1])
            if norm_temp!=0:
                temp = [settings.Item.MAGNET_STRENGTH*settings.Item.SPEED*temp[i]/norm_temp for i in [0,1]]
            self.change_direction(self.vx+temp[0],self.vy)
            self.v = norm(self.direction[0],self.direction[1])
        super().update(dt)