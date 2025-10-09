import pygame, settings, sound
from display import Display
from sprite import Sprite
from image import Image, GraphicData
from math import ceil
from settings import BulletTemplate, BULLET, ALIEN
from physics import Vector

class Bullet(Sprite):
    """Manage creation and properties of the player's and enemies' bullets"""

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
                boundary_behaviour: str | None = "vanish"):
        # speed, owner, damage allow overwriting their standard settings for given template
        # size only relevant for blubber
        self.template = template
        self.owner = owner or template.owner
        self.damage = damage or template.damage
        speed = speed if speed is not None else template.speed
        if vel is None:
            vel = Vector(0, -speed) if self.owner == "player" else Vector(0, speed)
        constraints = constraints or Display.screen_rect
        
        if template.name == "blubber":
            self.size = size or ALIEN.BLOB.energy
            self.damage = ceil((size / ALIEN.BLOB.energy) * template.damage)
            graphic = GraphicData(image = Image.blubber[size-1])
        else:
            graphic = GraphicData(path = f'images/bullet/{template.name}', scaling_width = template.width,
                        animation_type = template.animation_type, animation_time = template.animation_time)
        if self.template.name == "explosion":
            self.hit_enemies = pygame.sprite.Group()
        super().__init__(graphic = graphic, pos = pos, vel = vel, acc = acc,
            constraints = constraints, boundary_behaviour = boundary_behaviour)

    @classmethod
    def from_size(cls, size, **kwargs):
        mapping = {1: BULLET.BULLET1, 2: BULLET.BULLET2, 3: BULLET.BULLET3}
        return cls(mapping[size], **kwargs)

    def play_firing_sound(self):
        match self.template.name:
            case "1" | "2" | "3":
                sound.bullet.play()
            case "blubber":
                sound.blubber.play()
            case "g":
                sound.alienshoot1.play()
            case "explosion":
                sound.explosion.play()

    def update(self, dt):
        # timer, movement and animation get handled in the Sprite class
        super().update(dt)
        # explosions by missiles need to get deleted manually after their duration
        if self.graphic.animation_type == "vanish" and self.animation_timer.total_time > int(1000 * self.graphic.animation_time):
            self.kill()

    def reflect(self):
        sound.shield.stop()
        sound.shield_reflect.play()
        super().reflect(flip_x=True, flip_y=True)