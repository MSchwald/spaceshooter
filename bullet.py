import pygame, settings, sound
from display import Display
from sprite import Sprite
from image import Image
from math import ceil

class Bullet(Sprite):
    """A class to manage the bullets shot by the player or enemies"""

    def __init__(self, type, size=None, owner=None, damage=None, effect_time = None, image=None,
            v=None, grid=None, center=None, x=0, y=0, direction=None,
            constraints=None,
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
        if constraints is None:
            constraints = pygame.Rect([0, 0, Display.screen_width, Display.screen_height])
        if type in [1,2,3]:
            if image is None:
                image = Image.load(f'images/bullet/{type}.png')
        elif type == "blubber":
            sound.blubber.play()
            if size is None:
                size = settings.alien_energy["blob"]
            self.size = size
            image = Image.blubber[size-1]
            self.damage = ceil(size/settings.alien_energy["blob"]*settings.bullet_damage[type])
        elif type == "missile":
            frames = Image.load(f"images/bullet/explosion")
            animation_type = "vanish"
            animation_time = settings.missile_duration
            self.hit_enemies = pygame.sprite.Group()
        elif type == "g":
            sound.alienshoot1.play()
            frames = Image.load(f"images/bullet/g")
            animation_type = "once"
            animation_time = 0.5
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
        #timer, movement and animation get handled in the Sprite class
        super().update(dt)
        # explosions by missiles need to get deleted manually after their duration
        if self.effect_time and self.timer > self.effect_time:
                self.kill()

    def reflect(self):
        sound.shield.stop()
        sound.shield_reflect.play()
        if self.type == "blubber":
            self.direction = (-self.direction[0],-self.direction[1])
            self.change_image(Image.reflected_blubber[self.size-1])
        else:
            super().reflect(flip_x=True, flip_y=True)