from __future__ import annotations
import pygame
from sound import Sound
from settings import BulletTemplate, BULLET, ALIEN
from display import Display
from image import Image, GraphicData
from sprite import Sprite, BOUNDARY
from math import ceil
from physics import Vector

class Bullet(Sprite):
    """Manage creation and properties of the player's and enemies' bullets."""

    def __init__(self, template: BulletTemplate,
                speed: float | None = None,
                direction: Vector | None = None,
                pos: Vector | None = None,
                vel: Vector | None = None,
                acc: Vector = Vector(0, 0),
                owner: str | None = None,
                damage: int | None = None,
                size: int | None = None,
                constraints: pygame.Rect | None = None,
                boundary_behaviour: str | None = BOUNDARY.VANISH):
        """speed, owner, damage: allow for overwriting their default settings for given template.
        size: only used for blubber to determine the size of its sprite."""
        self.template = template
        self.owner = owner or template.owner
        self.damage = damage or template.damage
        speed = speed if speed is not None else template.speed
        if vel is None:
            vel = Vector(0, -speed) if self.owner == "player" else Vector(0, speed)
        constraints = constraints or Display.screen_rect
        graphic = GraphicData(path = f'images/bullet/{template.name}', scaling_width = template.width,
                        animation_type = template.animation_type, animation_time = template.animation_time)
        super().__init__(graphic = graphic, pos = pos, vel = vel, acc = acc,
            constraints = constraints, boundary_behaviour = boundary_behaviour)
        if template.name == "blubber":
            self.size = size or ALIEN.BLOB.energy
            scaling_factor = (ALIEN.BLOB.energy / self.size) ** (-1/3)
            self.graphic.image = self.graphic.image.scale_by(scaling_factor)
            self.damage = ceil((size / ALIEN.BLOB.energy) * template.damage)
        if self.template.name == "explosion":
            self.hit_enemies = pygame.sprite.Group()
        

    @classmethod
    def from_size(cls, size: int, **kwargs) -> Bullet:
        """Creates a ship bullet of a given size 1, 2 or 3"""
        mapping = {1: BULLET.BULLET1, 2: BULLET.BULLET2, 3: BULLET.BULLET3}
        return cls(mapping[size], **kwargs)

    def play_firing_sound(self):
        match self.template.name:
            case "1" | "2" | "3":
                Sound.bullet.play()
            case "blubber":
                Sound.blubber.play()
            case "g":
                Sound.alienshoot1.play()
            case "explosion":
                Sound.explosion.play()

    def reflect(self):
        """Reflecting bullets with shield sound effects."""
        Sound.shield.stop()
        Sound.shield_reflect.play()
        super().reflect(flip_x=True, flip_y=True)