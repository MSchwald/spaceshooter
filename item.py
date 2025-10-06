import pygame, sound
from image import Image, GraphicData
from sprite import Sprite
from display import Display
from math import hypot as norm
from settings import ItemType, ITEM

class Item(Sprite):
    """A class to manage the items"""

    def __init__(self, type: ItemType, level, **pos_kwargs):
        self.type = type
        self.level = level
        self.duration_ms = int(1000*type.duration) if type.duration is not None else None
        graphic = GraphicData(path = f'images/item/{str(type.name)}', scaling_width = type.size)
        super().__init__(graphic = graphic, direction=(0,1), v=type.speed,
                constraints=pygame.Rect([0, 0, Display.screen_width, Display.screen_height]),
                boundary_behaviour="vanish", **pos_kwargs)
        
    def play_collecting_sound(self):
        match self.type.name:
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
                temp = [ITEM.MAGNET.effect*self.type.speed*temp[i]/norm_temp for i in [0,1]]
            self.change_direction(self.vx+temp[0],self.vy)
            self.v = norm(self.direction[0],self.direction[1])
        super().update(dt)