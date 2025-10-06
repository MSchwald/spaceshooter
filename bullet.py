import pygame, settings, sound
from display import Display
from sprite import Sprite
from image import Image, GraphicData
from math import ceil
from settings import BulletType, BULLET, ALIEN

class Bullet(Sprite):
    """Manage creation and properties of the player's and enemies' bullets"""

    def __init__(self, type: BulletType,
                v=None, owner=None, damage=None, direction=None, size=None,
                constraints=None, boundary_behaviour="vanish", **pos_kwargs):
        # v, owner, damage, direction allow overwriting their standard settings for given BulletType
        # size only relevant for blubber
        self.type = type
        self.owner = owner or type.owner
        self.damage = damage or type.damage
        if direction is None:
            if self.owner == "player":
                direction = (0,-1)
            else:
                direction = (0,1)
        constraints = constraints or pygame.Rect(0, 0, Display.screen_width, Display.screen_height)
        v = v if v is not None else type.speed
        
        if type.name == "blubber":
            self.size = size or ALIEN.BLOB.energy
            self.damage = ceil(size / ALIEN.BLOB.energy*type.damage)
            graphic = GraphicData(image = Image.blubber[size-1])
        else:
            graphic = GraphicData(path = f'images/bullet/{type.name}', scaling_width = type.width,
                        animation_type = type.animation_type, animation_time = type.animation_time)
        if self.type.name == "explosion":
            self.hit_enemies = pygame.sprite.Group()
        super().__init__(graphic = graphic, v=v, direction=direction,
            constraints=constraints, boundary_behaviour=boundary_behaviour, **pos_kwargs)

    @classmethod
    def from_size(cls, size, **kwargs):
        match size:
            case 1: return Bullet(BULLET.BULLET1, **kwargs)
            case 2: return Bullet(BULLET.BULLET2, **kwargs)
            case 3: return Bullet(BULLET.BULLET3, **kwargs)

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
        if self.graphic.animation_type == "vanish" and self.timer > int(1000*self.graphic.animation_time):
            self.kill()

    def reflect(self):
        sound.shield.stop()
        sound.shield_reflect.play()
        if self.type.name == "blubber":
            self.direction = (-self.direction[0],-self.direction[1])
            self.change_image(Image.reflected_blubber[self.size-1])
        else:
            super().reflect(flip_x=True, flip_y=True)