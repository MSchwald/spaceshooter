import pygame, settings, sound
from pygame.locals import *
from image import Image
from sprite import Sprite
from bullet import Bullet
from display import Display


class Ship(Sprite):
    """A class to manage the ship."""

    def __init__(self, level, x=0, y=0, ship_lives=settings.ship_lives, rank=settings.ship_starting_rank):
        #level: needs access to the level object from the game file
        super().__init__(Image.load(f"images/ship/a-{rank}.png"), x=0, y=0, constraints=pygame.Rect(
            [0, 5/9*Display.screen_height, Display.screen_width, 4/9*Display.screen_height]), boundary_behaviour="clamp")
        self.level = level
        self.start_new_game(ship_lives, rank)

    def start_new_game(self, ship_lives=settings.ship_lives, rank=settings.ship_starting_rank):
        """Start new game"""
        self.reset_items()
        self.reset_stats(ship_lives, rank)
        self.reset_position()

    def reset_position(self):
        """Ship starts each level at the midbottom"""
        self.rect.midbottom = self.constraints.midbottom
        self.x, self.y = self.rect.x, self.rect.y

    def reset_stats(self, ship_lives=settings.ship_lives, rank=settings.ship_starting_rank):
        """Ship starts the game with given stats"""
        self.score = settings.starting_score
        self.set_rank(rank)
        self.lives = ship_lives

    def set_rank(self, rank):
        """Updates the rank and dependend variables of the ship"""
        self.rank = rank
        self.v = self.speed_factor*settings.rank_speed[rank]
        self.update_image()
        self.max_energy = settings.rank_energy[rank]
        self.energy = self.max_energy
        self.reset_firepoints()

    def reset_firepoints(self):
        """Resets where the ship shoots bullets, consistent with size changes of the ship"""
        if self.rank == 1:
            self.fire_points = [(self.w/2, 0)]
            self.bullet_sizes = [1]
        elif self.rank == 2:
            self.fire_points = [(9/106*self.w, 54/146*self.h),
                                (self.w/2, 0), (95/106*self.w, 54/146*self.h)]
            self.bullet_sizes = [1, 2, 1]
        elif self.rank == 3:
            self.fire_points = [(12/133*self.w, 71/178*self.h), (23/133*self.w, 49/178*self.h),
                                (self.w/2, 0), (109/133*self.w, 49/178*self.h), (120/133*self.w, 71/178*self.h)]
            self.bullet_sizes = [1, 2, 3, 2, 1]
        self.bullet_sizes = [min(3,n+self.bullets_buff) for n in self.bullet_sizes]

    def gain_rank(self):
        if self.rank < 3:
            self.set_rank(self.rank+1)

    def lose_rank(self):
        if self.rank > 1:
            self.reset_items()
            self.set_rank(self.rank-1)
        else:
            self.lose_life()

    def lose_life(self):
        self.lives -= 1
        if self.lives > 0:
            self.set_rank(1)
            self.reset_items()
            self.level.start()
            sound.lose_life.play()

    def get_damage(self, damage):
        self.energy = max(0,self.energy-damage)
        if self.energy == 0:
            self.lose_rank()

    def shoot_bullets(self):
        # if there aren't too many bullets from the ship on the screen yet
        if len(self.level.ship_bullets) < settings.max_bullets*(2*self.rank-1) and self.status != "shield":
            sound.bullet.play()
            # Takes Doppler effect into account to calculate the bullets' speed
            doppler = self.vy
            # Fires bullets
            for i in range(len(self.fire_points)):
                type = self.bullet_sizes[i]
                bullet = Bullet(type, v=settings.bullet_speed[type]-doppler,
                                        center=(self.x+self.fire_points[i][0],self.y+self.fire_points[i][1]))
                self.level.bullets.add(bullet)
                self.level.ship_bullets.add(bullet)

    def control(self, keys):
        if self.status == "shield":
            self.change_direction(0,0)
        elif self.status == "inverse_controlls":
            self.change_direction(-keys[K_d]+keys[K_a], -keys[K_s]+keys[K_w])
        else:
            self.change_direction(keys[K_d]-keys[K_a], keys[K_s]-keys[K_w])

    def update_image(self):
        letter = {"normal":"a", "inverse_controlls":"g", "shield":"h", "magnetic":"e"}[self.status]
        self.change_image(Image.load(f'images/ship/{letter}-{self.rank}.png').scale_by(self.size_factor))
        self.reset_firepoints()

    def collect_item(self, type):
        match type:
            case "bullets_buff":
                self.bullets_buff += 1
                self.reset_firepoints()
                sound.item_collect.play()
            case "hp_plus":
                self.energy = min(self.max_energy, self.energy+settings.hp_plus)
                sound.good_item.play()
            case "invert_controlls":
                if self.status == "inverse_controlls":
                    self.status = "normal"
                else:
                    self.status = "inverse_controlls"
                    self.controlls_timer = 1000*settings.invert_controlls_duration
                    sound.bad_item.play()
                self.update_image()
            case "life_minus":
                self.lives -= 1
                if self.lives > 0:
                    sound.lose_life.play()
            case "life_plus":
                self.lives += 1
                sound.extra_life.play()
            case "magnet":
                self.magnet = True
                self.status = "magnetic"
                self.update_image()
                sound.item_collect.play()
            case "missile":
                self.missiles += 1
                sound.collect_missile.play()
            case "score_buff":
                if self.score_factor == 1:
                    self.score_buff_timer = 1000*settings.score_buff_duration
                self.score_factor *= settings.item_score_buff
                sound.item_collect.play()
            case "shield":
                self.shield_timer = min(1000*settings.max_shield_duration, self.shield_timer+1000*settings.shield_duration)
                sound.good_item.play()
            case "ship_buff":
                self.gain_rank()
                sound.ship_level_up.play()
            case "size_minus":
                sound.shrink.play()
                if self.size_factor*settings.item_size_minus>=0.3:
                    self.size_factor *= settings.item_size_minus
                    self.update_image()
                    if self.size_factor != 1:
                        self.size_change_timer = 1000*settings.size_change_duration
            case "size_plus":
                sound.grow.play()
                if self.size_factor*settings.item_size_plus<=1/0.3:
                    self.size_factor *= settings.item_size_plus
                    self.update_image()
                    if self.size_factor != 1:
                        self.size_change_timer = 1000*settings.size_change_duration
            case "speed_buff":
                sound.item_collect.play()
                if self.v*settings.speed_buff < settings.bullet_speed[1]:
                    self.speed_factor = settings.speed_buff
                    self.v = self.speed_factor*settings.rank_speed[self.rank]
                    if self.speed_factor != 1:
                        self.speed_change_timer = 1000*settings.speed_change_duration
            case "speed_nerf":
                sound.bad_item.play()
                self.speed_factor = settings.speed_nerf
                self.v = self.speed_factor*settings.rank_speed[self.rank]
                if self.speed_factor != 1:
                    self.speed_change_timer = 1000*settings.speed_change_duration

    def activate_shield(self):
        if self.shield_timer > 0:
            sound.shield.play()
            self.last_status = self.status
            self.status = "shield"
            self.update_image()

    def deactivate_shield(self):
        if self.status == "shield":
            self.status = self.last_status
            self.update_image()

    def shoot_missile(self, position):
        """shoots missile to position = (x,y)"""
        if self.missiles > 0:
            sound.explosion.play()
            self.missiles -= 1
            self.level.bullets.add(Bullet("missile", center=position))

    def get_points(self, points):
        self.score += int(self.score_factor*points)

    def reset_items(self):
        self.bullets_buff = 0
        self.speed_factor = 1
        self.magnet = False
        self.missiles = settings.starting_missiles
        self.score_factor = 1
        self.shield_timer = 1000*settings.shield_starting_timer
        self.size_factor = 1
        self.status = "normal"
        self.last_status = "normal"

    def update(self, dt):
        if self.status == "shield":
            self.shield_timer = max(self.shield_timer - dt, 0)
            if self.shield_timer == 0:
                self.status = self.last_status
                self.update_image()
        if self.score_factor != 1:
            self.score_buff_timer -= dt
            if self.score_buff_timer <= 0:
                self.score_factor = 1
        if self.speed_factor != 1:
            self.speed_change_timer -= dt
            if self.speed_change_timer <= 0:
                self.speed_factor = 1
                self.v = settings.rank_speed[self.rank]
        if self.size_factor != 1:
            self.size_change_timer -= dt
            if self.size_change_timer <= 0:
                self.size_factor = 1
                self.update_image()
        if self.status == "inverse_controlls":
            self.controlls_timer -= dt
            if self.controlls_timer <= 0:
                self.status = "normal"
                self.update_image()
        super().update(dt)