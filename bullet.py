import pygame
from pygame.locals import *
import settings
import image
from sprite import Sprite
from image import Image

class Bullet(Sprite):
    """A class to manage the bullets shot by the player or enemies"""

    def __init__(self, type, owner=None, damage=None, effect_time = None, image=None,
            v=None, grid=None, center=None, x=0, y=0, direction=None,
            constraints=pygame.Rect(0, 0, settings.screen_width, settings.screen_height),
            boundary_behaviour="vanish",
            animation_type=None, frames=None, fps=None, animation_time=None):
        self.type = type
        if owner is None:
            owner = settings.bullet_owner[type]
        self.owner = owner
        if damage is None:
            damage = settings.bullet_damage[type]
        self.damage = damage
        if effect_time is None:
            effect_time = settings.bullet_effect_time[type]
        self.effect_time = effect_time
        if type != "missile":
            if image is None:
                image = Image.load(f'images/bullet/{type}.png', scaling_width = settings.bullet_width[type])
        else:
            frames = [Image.load(f"images/bullet/explosion{n}.png", scaling_factor=settings.missile_explosion_size/810) for n in range(6)]
            animation_type = "vanish"
            animation_time = settings.missile_duration
        if v is None:
            v = settings.bullet_speed[type]
        if direction is None:
            if self.owner == "player":
                direction = (0,-1)
            else:
                direction = (0,1)
        super().__init__(image, grid=grid, center=center, x=x, y=y, v=v, direction=direction,
            constraints=constraints, boundary_behaviour=boundary_behaviour,
            animation_type=animation_type, frames=frames, animation_time=animation_time)

    def update(self, dt):
        super().update(dt)
        if self.effect_time and self.timer > self.effect_time:
                self.kill()