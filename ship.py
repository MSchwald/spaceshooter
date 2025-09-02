import pygame
from pygame.locals import *
import settings
from image import Image
from sprite import Sprite
from bullet import Bullet


class Ship(Sprite):
    """A class to manage the ship."""

    def __init__(self, x=0, y=0, ship_lives=settings.ship_lives, ship_level=settings.ship_starting_level):
        super().__init__(Image.load(f"images/ship/a-{ship_level}.png", scaling_width=settings.ship_width[ship_level]), x=0, y=0, constraints=pygame.Rect(
            settings.ship_constraints), boundary_behaviour="clamp")
        # initializes an empty group of sprites for the bullets shot by the ship
        self.bullets = pygame.sprite.Group()
        self.start_new_game(ship_lives, ship_level)

    def start_new_game(self, ship_lives=settings.ship_lives, ship_level=settings.ship_starting_level):
        """Start new game"""
        # Delete all bullets
        self.bullets.empty()
        self.reset_items()
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
        self.update_image()
        self.max_energy = settings.level_energy[ship_level]
        self.energy = self.max_energy
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
        self.bullet_sizes = [min(3,n+self.bullets_buff) for n in self.bullet_sizes]

    def gain_level(self):
        if self.level < 3:
            self.set_level(self.level+1)

    def lose_level(self):
        if self.level > 1:
            self.reset_items()
            self.set_level(self.level-1)
        else:
            self.lose_life()

    def lose_life(self):
        self.reset_items()
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
                self.x+self.fire_points[i][0]-settings.bullet_width[self.bullet_sizes[i]]/2, self.y+self.fire_points[i][1], speed, self.bullet_sizes[i]))

    def control(self, keys):
        self.change_direction(self.controlls_factor*(keys[K_d]-keys[K_a]), self.controlls_factor*(keys[K_s]-keys[K_w]))

    def update_image(self):
        if self.status == "normal":
            self.change_image(Image.load(f'images/ship/a-{self.level}.png').scale_by(self.size_factor))
        elif self.status == "inverse_controlls":
            self.change_image(Image.load(f'images/ship/g-{self.level}.png').scale_by(self.size_factor))
        elif self.status == "shield":
            self.change_image(Image.load(f'images/ship/h-{self.level}.png').scale_by(self.size_factor))
        elif self.status == "magnetic":
            self.change_image(Image.load(f'images/ship/e-{self.level}.png').scale_by(self.size_factor))
        self.reset_firepoints()

    def collect_item(self, type):
        if type == "bullets_buff":
            self.bullets_buff += 1
        elif type == "hp_plus":
            self.energy += settings.hp_plus
        elif type == "invert_controlls":
            self.controlls_factor *= -1
            if self.status == "inverse_controlls":
                self.status = "normal"
            else:
                self.status = "inverse_controlls"
            self.update_image()
        elif type == "life_minus":
            self.lose_life()
        elif type == "life_plus":
            self.lives += 1
        elif type == "magnet":
            self.magnet = True
            self.status = "magnetic"
            self.update_image()
        elif type == "missile":
            self.missiles += 1
        elif type == "score_buff":
            self.score_factor *= settings.item_score_buff
        elif type == "shield":
            self.shields += 1
        elif type == "ship_buff":
            self.gain_level()
        elif type == "size_minus":
            if self.size_factor*settings.item_size_minus>=0.3:
                self.size_factor *= settings.item_size_minus
                image = Image.load(f"images/ship/a-{self.level}.png")
                self.update_image()
        elif type == "size_plus":
            if self.size_factor*settings.item_size_plus<=1/0.3:
                self.size_factor *= settings.item_size_plus
                self.update_image()
        elif type == "speed_buff":
            self.speed_factor = settings.speed_buff
            self.v *= self.speed_factor
        elif type == "speed_nerf":
            self.speed_factor = settings.speed_nerf
            self.v *= self.speed_factor

    def reset_items(self):
        self.bullets_buff = 0
        self.controlls_factor = 1
        self.speed_factor = 1
        self.magnet = False
        self.missiles = 0
        self.score_factor = 1
        self.shields = 0
        self.size_factor = 1
        self.status = "normal"
        
