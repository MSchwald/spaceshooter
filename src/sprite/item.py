from __future__ import annotations
import pygame
from sound import Sound
from display import Display
from settings import ItemTemplate, ITEM, SHIP_STATUS
from image import Image, GraphicData
from sprite import Sprite, BOUNDARY
from physics import Vector, norm

class Item(Sprite):
    """Manage sprites, spawning and properties of items."""

    def __init__(self, template: ItemTemplate,
                level: Level,
                pos: Vector | None = None,
                vel: Vector | None = None,
                acc: Vector = Vector(0, 0),
                constraints: pygame.Rect | None = None,
                boundary_behaviour: str | None = BOUNDARY.VANISH):
        self.template = template
        self.level = level
        vel = vel or Vector(0, template.speed)
        constraints = constraints or Display.screen_rect
        self.duration_ms = int(1000 * template.duration) if template.duration is not None else None
        graphic = GraphicData(path = f'images/item/{str(template.name)}', scaling_width = template.size)
        super().__init__(graphic = graphic, pos = pos, vel = vel, acc = acc,
                constraints = constraints, boundary_behaviour = boundary_behaviour)
        
    def play_collecting_sound(self):
        match self.template.name:
            case "bullets_buff" | "magnet" | "score_buff" | "speed_buff":
                Sound.item_collect.play()
            case "hp_plus" | "shield":
                Sound.good_item.play()
            case "life_plus":
                Sound.extra_life.play()
            case "missile":
                Sound.collect_missile.play()
            case "ship_buff":
                Sound.ship_level_up.play()
            case "size_plus":
                Sound.grow.play()
            case "size_minus":
                Sound.shrink.play()
            case "speed_nerf":
                Sound.bad_item.play()

    def update(self, dt: int):
        """Calculate the state of the item after dt passed ms.
        If the magnet effect is active, item's get horizontally
        accelerated towards the ship."""
        if self.level.ship.status == SHIP_STATUS.MAGNETIC:
            dpos = self.level.ship.center-self.center
            dist = norm(dpos)
            if dist != 0:
                acc = ITEM.MAGNET.effect * self.template.speed * dpos / dist
                self.acc = Vector(acc.x, 0)
        super().update(dt)