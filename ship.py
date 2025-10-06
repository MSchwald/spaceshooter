import pygame, sound
from settings import KEY, BULLET, SHIP
from image import Image, GraphicData
from sprite import Sprite
from bullet import Bullet
from display import Display


class Ship(Sprite):
    """Manage the ship's position and status properties"""

    def __init__(self, level, ship_lives=SHIP.LIVES, rank=SHIP.RANK):
        # level: needs access to the level object from the game file
        graphic = GraphicData(path = f"images/ship/a-{rank}.png", scaling_width = SHIP.WIDTH[rank])
        super().__init__(graphic = graphic,
            constraints=pygame.Rect(0, 5/9*Display.screen_height, Display.screen_width, 4/9*Display.screen_height),
            boundary_behaviour="clamp")
        self.level = level
        self.start_new_game(ship_lives, rank)

    def start_new_game(self, ship_lives=SHIP.LIVES, rank=SHIP.RANK):
        """Start new game"""
        self.reset_item_effects()
        self.reset_stats(ship_lives, rank)
        self.reset_position()

    def reset_position(self):
        """Ship starts each level at the midbottom"""
        self.rect.midbottom = self.constraints.midbottom
        self.x, self.y = self.rect.x, self.rect.y

    def reset_stats(self, ship_lives=SHIP.LIVES, rank=SHIP.RANK):
        """Ship starts the game with given stats"""
        self.score = SHIP.SCORE
        self.set_rank(rank)
        self.lives = ship_lives

    def set_rank(self, rank):
        """Updates the rank and dependend variables of the ship"""
        self.rank = rank
        self.v = self.speed_factor*SHIP.SPEED[rank]
        self.update_graphic()
        self.max_energy = SHIP.ENERGY[rank]
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
        if len(self.level.ship_bullets) < SHIP.MAX_BULLETS*(2*self.rank-1) and self.status != "shield":
            # Takes Doppler effect into account to calculate the bullets' speed
            doppler = self.vy
            # Fires bullets
            for (fp_x,fp_y), size in zip(self.fire_points, self.bullet_sizes):
                bullet = Bullet.from_size(size, center=(self.x+fp_x,self.y+fp_y))
                bullet.v -= doppler
                self.level.bullets.add(bullet)
            bullet.play_firing_sound()

    def control(self, keys):
        if keys[KEY.SHIELD]:
            if self.status != "shield":
                self.activate_shield()
                self.direction = (0,0)
        else:
            if self.status == "shield":
                self.deactivate_shield()
            if self.status == "inverse_controls":
                self.direction = (-keys[KEY.RIGHT]+keys[KEY.LEFT], -keys[KEY.DOWN]+keys[KEY.UP])
            else:
                self.direction = (keys[KEY.RIGHT]-keys[KEY.LEFT], keys[KEY.DOWN]-keys[KEY.UP])

    def update_graphic(self):
        letter = {"normal":"a", "inverse_controls":"g", "shield":"h", "magnetic":"e"}[self.status]
        self.graphic = GraphicData(path = f"images/ship/{letter}-{self.rank}.png", scaling_width = SHIP.WIDTH[self.rank])
        self.change_image(self.graphic.image.scale_by(self.size_factor))

    def collect_item(self, item):
        item.play_collecting_sound()
        match item.type.name:
            case "bullets_buff": self.bullets_buff += 1
            case "hp_plus": self.energy = min(self.max_energy, self.energy+item.type.effect)
            case "invert_controls":
                if self.status == "inverse_controls":
                    self.status = "normal"
                else:
                    self.status = "inverse_controls"
                    self.controls_timer = item.duration_ms
                    sound.bad_item.play()
                self.update_graphic()
            case "life_minus":
                self.lives -= 1
                if self.lives > 0:
                    sound.lose_life.play()
            case "life_plus": self.lives += 1
            case "magnet":
                self.magnet = True
                self.status = "magnetic"
                self.update_graphic()
            case "missile": self.missiles += 1
            case "score_buff":
                if self.score_factor == 1:
                    self.score_buff_timer = item.duration_ms
                self.score_factor *= item.type.effect
            case "shield":
                self.shield_timer = min(1000*SHIP.MAX_SHIELD_DURATION, self.shield_timer+1000*item.type.effect)
            case "ship_buff": self.gain_rank()
            case "size_minus":
                if self.size_factor * item.type.effect >= 0.3:
                    self.size_factor *= item.type.effect
                    self.update_graphic()
                    if self.size_factor != 1:
                        self.size_change_timer = item.duration_ms
            case "size_plus":
                if self.size_factor * item.type.effect <= 1/0.3:
                    self.size_factor *= item.type.effect
                    self.update_graphic()
                    if self.size_factor != 1:
                        self.size_change_timer = item.duration_ms
            case "speed_buff":
                if self.v * item.type.effect < BULLET.BULLET1.speed:
                    self.speed_factor *= item.type.effect
                    self.v = self.speed_factor * SHIP.SPEED[self.rank]
                    if self.speed_factor != 1:
                        self.speed_change_timer = item.duration_ms
            case "speed_nerf":
                self.speed_factor *= item.type.effect
                self.v = self.speed_factor * SHIP.SPEED[self.rank]
                if self.speed_factor != 1:
                    self.speed_change_timer = item.duration_ms

    def activate_shield(self):
        if self.shield_timer > 0:
            sound.shield.play()
            self.last_status, self.status = self.status, "shield"
            self.update_graphic()

    def deactivate_shield(self):
        if self.status == "shield":
            self.status = self.last_status
            self.update_graphic()

    def shoot_missile(self, position):
        """shoots missile to position = (x,y)"""
        if self.missiles > 0:
            self.missiles -= 1
            missile = Bullet(BULLET.MISSILE, center=position)
            self.level.bullets.add(missile)
            missile.play_firing_sound()

    def get_points(self, points):
        self.score += int(self.score_factor*points)

    def reset_item_effects(self):
        self.bullets_buff = 0
        self.speed_factor = 1
        self.magnet = False
        self.missiles = SHIP.STARTING_MISSILES
        self.score_factor = 1
        self.shield_timer = 1000*SHIP.SHIELD_STARTING_TIMER
        self.size_factor = 1
        self.status = "normal"
        self.last_status = "normal"

    def update(self, dt):
        if self.status == "shield":
            self.shield_timer = max(self.shield_timer - dt, 0)
            if self.shield_timer == 0:
                self.status = self.last_status
                self.update_graphic()
        if self.score_factor != 1:
            self.score_buff_timer -= dt
            if self.score_buff_timer <= 0:
                self.score_factor = 1
        if self.speed_factor != 1:
            self.speed_change_timer -= dt
            if self.speed_change_timer <= 0:
                self.speed_factor = 1
                self.v = SHIP.SPEED[self.rank]
        if self.size_factor != 1:
            self.size_change_timer -= dt
            if self.size_change_timer <= 0:
                self.size_factor = 1
                self.update_graphic()
        if self.status == "inverse_controls":
            self.controls_timer -= dt
            if self.controls_timer <= 0:
                self.status = "normal"
                self.update_graphic()
        super().update(dt)