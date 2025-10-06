import pygame, settings, sound
from display import Display
from sprite import Sprite
from image import Image
from math import ceil
from settings import BulletType, BULLET

class Bullet(Sprite):
    """Manage creation and properties of the player's and enemies' bullets"""

    def __init__(self, type: BulletType, size=None, owner=None, damage=None, image=None,
            v=None, grid=None, center=None, x=0, y=0, direction=None,
            constraints=None,
            boundary_behaviour="vanish"):
        self.type = type
        self.owner = owner or type.owner
        self.damage = damage or type.damage
        constraints = constraints or pygame.Rect(0, 0, Display.screen_width, Display.screen_height)
        v = v if v is not None else type.speed
        if direction is None:
            if self.owner == "player":
                direction = (0,-1)
            else:
                direction = (0,1)
        if type.name == "blubber":
            self.size = size or settings.ALIEN.BLOB.energy
            image = Image.blubber[size-1]
            self.damage = ceil(size/settings.ALIEN.BLOB.energy*type.damage)
            frames = None
        else:
            if type.animation_type is None:
                image = Image.load(f'images/bullet/{type.name}.png')
                frames = None
            else:
                image = None
                frames = Image.load(f"images/bullet/{type.name}")
                if self.type.name == "explosion":
                    self.hit_enemies = pygame.sprite.Group()
        animation_type, animation_time = type.animation_type, type.animation_time
        super().__init__(image, grid=grid, center=center, x=x, y=y, v=v, direction=direction,
            constraints=constraints, boundary_behaviour=boundary_behaviour,
            animation_type=animation_type, frames=frames, animation_time=animation_time)

    @classmethod
    def from_size(cls, size, **kwargs):
        return [Bullet(BULLET.BULLET1, **kwargs), Bullet(BULLET.BULLET2, **kwargs), Bullet(BULLET.BULLET3, **kwargs)][size-1]

    def play_firing_sound(self):
        match self.type.name:
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
        if self.animation_type == "vanish" and self.timer > int(1000*self.animation_time):
            self.kill()

    def reflect(self):
        sound.shield.stop()
        sound.shield_reflect.play()
        if self.type.name == "blubber":
            self.direction = (-self.direction[0],-self.direction[1])
            self.change_image(Image.reflected_blubber[self.size-1])
        else:
            super().reflect(flip_x=True, flip_y=True)