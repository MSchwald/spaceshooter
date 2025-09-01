import pygame
from pygame.locals import *
import settings
from image import Image
from sprite import Sprite
from bullet import Bullet


class Ship(Sprite):
    """A class to manage the ship."""

    def __init__(self, x=0, y=0, ship_lives=settings.ship_lives, ship_level=settings.ship_starting_level):
        super().__init__(Image.load(f"images/ship/a-{ship_level}.PNG"), x=0, y=0, constraints=pygame.Rect(
            settings.ship_constraints), boundary_behaviour="clamp")
        # initializes an empty group of sprites for the bullets shot by the ship
        self.bullets = pygame.sprite.Group()
        self.start_new_game(ship_lives, ship_level)

    def start_new_game(self, ship_lives=settings.ship_lives, ship_level=settings.ship_starting_level):
        """Start new game"""
        # Delete all bullets
        self.bullets.empty()
        self.reset_stats(ship_lives, ship_level)
        self.reset_position()

    def reset_position(self):
        """Ship starts each level at the midbottom"""
        self.rect.midbottom = self.constraints.midbottom
        self.x, self.y = self.rect.x, self.rect.y

    def reset_stats(self, ship_lives=settings.ship_lives, ship_level=settings.ship_starting_level):
        """Ship starts the game with given stats"""
        self.score = settings.starting_score
        self.set_level(ship_level)
        self.lives = settings.ship_lives

    def set_level(self, ship_level):
        """Updates the level and dependend private variables"""
        self.level = ship_level
        self.v = settings.level_speed[ship_level]
        self.change_image(Image.load(f'images/ship/a-{ship_level}.png'))
        self.energy = settings.level_energy[ship_level]
        self.reset_firepoints()

    def reset_firepoints(self):
        """Resets where the ship shoots bullets, consistent with size changes of the ship"""
        if self.level == 1:
            self.fire_points = [(self.w/2, 0)]
            self.bullet_sizes = [1]
        elif self.level == 2:
            self.fire_points = [(9/106*self.w, 54/146*self.h),
                                (self.w/2, 0), (95/106*self.w, 54/146*self.h)]
            self.bullet_sizes = [1, 2, 1]
        elif self.level == 3:
            self.fire_points = [(12/133*self.w, 71/178*self.h), (23/133*self.w, 49/178*self.h),
                                (self.w/2, 0), (109/133*self.w, 49/178*self.h), (120/133*self.w, 71/178*self.h)]
            self.bullet_sizes = [1, 2, 3, 2, 1]
        self.bullet_width = [Image.load(f"images/bullet/{i}.png").w for i in self.bullet_sizes]

    def gain_level(self):
        if self.level < 3:
            self.set_level(self.level+1)

    def lose_level(self):
        if self.level > 1:
            self.set_level(self.level-1)
        else:
            self.lose_life()

    def lose_life(self):
        self.lives -= 1
        if self.lives > 0:
            self.set_level(1)

    def get_damage(self, damage):
        self.energy = max(0,self.energy-damage)
        if self.energy == 0:
            self.lose_level()

    def shoot_bullets(self):
        # Takes Doppler effect into account to calculate the bullets' speed
        speed = settings.bullet_speed
        if self.direction[1] != 0:
            speed -= self.v*self.direction[1]/self._norm
        # Fires bullets
        for i in range(len(self.fire_points)):
            self.bullets.add(Bullet(
                self.x+self.fire_points[i][0]-self.bullet_width[i]/2, self.y+self.fire_points[i][1], speed, self.bullet_sizes[i]))

    def control(self, keys):
        self.change_direction(keys[K_d]-keys[K_a], keys[K_s]-keys[K_w])
