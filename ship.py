import pygame, settings, sound
from settings import Key, BULLET1, BULLET2, BULLET3, MISSILE
from image import Image
from sprite import Sprite
from bullet import Bullet
from display import Display


class Ship(Sprite):
    """A class to manage the ship."""

    def __init__(self, level, x=0, y=0, ship_lives=settings.Ship.LIVES, rank=settings.Ship.RANK):
        #level: needs access to the level object from the game file
        super().__init__(Image.load(f"images/ship/a-{rank}.png"), x=0, y=0,
            constraints=pygame.Rect(0, 5/9*Display.screen_height, Display.screen_width, 4/9*Display.screen_height),
            boundary_behaviour="clamp")
        self.level = level
        self.start_new_game(ship_lives, rank)

    def start_new_game(self, ship_lives=settings.Ship.LIVES, rank=settings.Ship.RANK):
        """Start new game"""
        self.reset_item_effects()
        self.reset_stats(ship_lives, rank)
        self.reset_position()

    def reset_position(self):
        """Ship starts each level at the midbottom"""
        self.rect.midbottom = self.constraints.midbottom
        self.x, self.y = self.rect.x, self.rect.y

    def reset_stats(self, ship_lives=settings.Ship.LIVES, rank=settings.Ship.RANK):
        """Ship starts the game with given stats"""
        self.score = settings.Ship.SCORE
        self.set_rank(rank)
        self.lives = ship_lives

    def set_rank(self, rank):
        """Updates the rank and dependend variables of the ship"""
        self.rank = rank
        self.v = self.speed_factor*settings.Ship.SPEED[rank]
        self.update_image()
        self.max_energy = settings.Ship.ENERGY[rank]
        self.energy = self.max_energy

    def gain_rank(self):
        if self.rank < 3:
            self.set_rank(self.rank+1)

    def lose_rank(self):
        if self.rank > 1:
            self.reset_item_effects()
            self.set_rank(self.rank-1)
        else:
            self.lose_life()

    def lose_life(self):
        self.lives -= 1
        if self.lives > 0:
            self.set_rank(1)
            self.reset_item_effects()
            self.level.start_current()
            sound.lose_life.play()

    def get_damage(self, damage):
        self.energy = max(0,self.energy-damage)
        if self.energy == 0:
            self.lose_rank()

    @property
    def default_fire_points(self):
        """fire points depending only on the original ship sprites"""
        match self.rank:
            case 1: return [(51.5,0)]
            case 2: return [(9,54),(53,0),(95,54)]
            case 3: return [(12,71),(23,49),(66.5,0),(109,49),(120,71)]

    @property
    def default_width(self):
        match self.rank:
            case 1: return 103
            case 2: return 106
            case 3: return 133

    @property
    def default_height(self):
        match self.rank:
            case 1: return 79
            case 2: return 146
            case 3: return 178

    @property
    def fire_points(self):
        """Rescale where the ship shoots bullets, consistent with size changes of the ship"""
        return [(x*self.w/self.default_width,y*self.h/self.default_height) for (x,y) in self.default_fire_points]
        
    @property
    def bullet_sizes(self):
        match self.rank:
            case 1: sizes = [1]
            case 2: sizes = [1,2,1]
            case 3: sizes = [1,2,3,2,1]
        return [min(3, size + self.bullets_buff) for size in sizes]

    def shoot_bullets(self):
        # if there aren't too many bullets from the ship on the screen yet
        if len(self.level.ship_bullets) < settings.Ship.MAX_BULLETS*(2*self.rank-1) and self.status != "shield":
            # Takes Doppler effect into account to calculate the bullets' speed
            doppler = self.vy
            # Fires bullets
            for (fp_x,fp_y), size in zip(self.fire_points, self.bullet_sizes):
                bullet = Bullet.from_size(size, v=Bullet.from_size(size).v-doppler,center=(self.x+fp_x,self.y+fp_y))
                self.level.bullets.add(bullet)
            bullet.play_firing_sound()

    def control(self, keys):
        if keys[Key.SHIELD]:
            if self.status != "shield":
                self.activate_shield()
                self.change_direction(0,0)
        else:
            if self.status == "shield":
                self.deactivate_shield()
            if self.status == "inverse_controls":
                self.change_direction(-keys[Key.RIGHT]+keys[Key.LEFT], -keys[Key.DOWN]+keys[Key.UP])
            else:
                self.change_direction(keys[Key.RIGHT]-keys[Key.LEFT], keys[Key.DOWN]-keys[Key.UP])

    def update_image(self):
        letter = {"normal":"a", "inverse_controls":"g", "shield":"h", "magnetic":"e"}[self.status]
        self.change_image(Image.load(f'images/ship/{letter}-{self.rank}.png').scale_by(self.size_factor))

    def collect_item(self, item):
        item.play_collecting_sound()
        match item.type:
            case "bullets_buff": self.bullets_buff += 1
            case "hp_plus": self.energy = min(self.max_energy, self.energy+settings.Item.HP_PLUS)
            case "invert_controls":
                if self.status == "inverse_controls":
                    self.status = "normal"
                else:
                    self.status = "inverse_controls"
                    self.controls_timer = item.effect_duration
                    sound.bad_item.play()
                self.update_image()
            case "life_minus":
                self.lives -= 1
                if self.lives > 0:
                    sound.lose_life.play()
            case "life_plus": self.lives += 1
            case "magnet":
                self.magnet = True
                self.status = "magnetic"
                self.update_image()
            case "missile": self.missiles += 1
            case "score_buff":
                if self.score_factor == 1:
                    self.score_buff_timer = item.effect_duration
                self.score_factor *= settings.Item.SCORE_BUFF
            case "shield":
                self.shield_timer = min(1000*settings.Ship.MAX_SHIELD_DURATION, self.shield_timer+1000*settings.Item.SHIELD_DURATION)
            case "ship_buff": self.gain_rank()
            case "size_minus":
                if self.size_factor*settings.Item.SIZE_MINUS>=0.3:
                    self.size_factor *= settings.Item.SIZE_MINUS
                    self.update_image()
                    if self.size_factor != 1:
                        self.size_change_timer = item.effect_duration
            case "size_plus":
                if self.size_factor*settings.Item.SIZE_PLUS<=1/0.3:
                    self.size_factor *= settings.Item.SIZE_PLUS
                    self.update_image()
                    if self.size_factor != 1:
                        self.size_change_timer = item.effect_duration
            case "speed_buff":
                if self.v*settings.Item.SPEED_BUFF < settings.BULLET1.speed:
                    self.speed_factor = settings.Item.SPEED_BUFF
                    self.v = self.speed_factor*settings.Ship.SPEED[self.rank]
                    if self.speed_factor != 1:
                        self.speed_change_timer = item.effect_duration
            case "speed_nerf":
                self.speed_factor = settings.Item.SPEED_NERF
                self.v = self.speed_factor*settings.Ship.SPEED[self.rank]
                if self.speed_factor != 1:
                    self.speed_change_timer = item.effect_duration

    def activate_shield(self):
        if self.shield_timer > 0:
            sound.shield.play()
            self.last_status, self.status = self.status, "shield"
            self.update_image()

    def deactivate_shield(self):
        if self.status == "shield":
            self.status = self.last_status
            self.update_image()

    def shoot_missile(self, position):
        """shoots missile to position = (x,y)"""
        if self.missiles > 0:
            self.missiles -= 1
            missile = Bullet(MISSILE, center=position)
            self.level.bullets.add(missile)
            missile.play_firing_sound()

    def get_points(self, points):
        self.score += int(self.score_factor*points)

    def reset_item_effects(self):
        self.bullets_buff = 0
        self.speed_factor = 1
        self.magnet = False
        self.missiles = settings.Ship.STARTING_MISSILES
        self.score_factor = 1
        self.shield_timer = 1000*settings.Ship.SHIELD_STARTING_TIMER
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
                self.v = settings.Ship.SPEED[self.rank]
        if self.size_factor != 1:
            self.size_change_timer -= dt
            if self.size_change_timer <= 0:
                self.size_factor = 1
                self.update_image()
        if self.status == "inverse_controls":
            self.controls_timer -= dt
            if self.controls_timer <= 0:
                self.status = "normal"
                self.update_image()
        super().update(dt)