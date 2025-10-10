from __future__ import annotations
import pygame, sound
from settings import KEY, BULLET, SHIP
from display import Display
from image import Image, GraphicData
from sprite import Sprite
from bullet import Bullet
from timer import ActionTimer
from physics import Vector, normalize

class Ship(Sprite):
    """Manage the ship's position, status properties and item effects."""

    def __init__(self, level: Level,
                        lives: int = SHIP.LIVES,
                        rank: int = SHIP.RANK):
        # Ship has access to all level objects
        self.level = level
        
        # Load the ship's starting properties and sprite
        self.lives = lives
        self.rank = rank
        self.score = SHIP.SCORE
        self.energy = self.max_energy
        graphic = GraphicData(path = f"images/ship/a-{rank}.png", scaling_width = SHIP.WIDTH[rank])
        super().__init__(graphic = graphic,
            constraints = Display.grid_rect(0, 5, 16, 4), boundary_behaviour = "clamp")
        self.reset_pos()

        # Initiate timers for shield and item effects
        self.shield_timer = ActionTimer()
        self.controls_timer = ActionTimer()
        self.score_buff_timer = ActionTimer()
        self.size_change_timer = ActionTimer()
        self.speed_change_timer = ActionTimer()
        self.timers = (self.shield_timer, self.controls_timer, self.score_buff_timer,
                    self.size_change_timer, self.speed_change_timer)
        
        # Initiate parameters for item effects
        self.reset_item_effects()

    def start_new_game(self, lives=SHIP.LIVES, rank=SHIP.RANK):
        """Reset the ship to it's default starting settings."""
        self.reset_item_effects()
        self.reset_stats(lives, rank)
        self.reset_pos()

    def reset_pos(self):
        """Ship starts each level at the midbottom of the screen."""
        self.spawn(pos = Vector(self.constraints.centerx - self.w / 2,
                                    self.constraints.bottom - self.h))

    def reset_stats(self, lives=SHIP.LIVES, rank=SHIP.RANK):
        """The ship starts the game with given stats."""
        self.score = SHIP.SCORE
        self.set_rank(rank)
        self.lives = lives

    def set_rank(self, rank):
        """Changes the rank and updates dependend properties of the ship."""
        self.rank = rank
        self.update_graphic()
        self.energy = self.max_energy

    @property
    def max_energy(self) -> int:
        """The maximal energy of the ship depends on it's current rank"""
        return SHIP.ENERGY[self.rank]

    @property
    def shield_time(self) -> int:
        """Currently remaining shield time."""
        return self.shield_timer.remaining_time

    # Methods to update rank, lives and energy of the ship
    def gain_rank(self):
        if self.rank < 3:
            self.set_rank(self.rank + 1)

    def lose_rank(self):
        if self.rank > 1:
            self.reset_item_effects()
            self.set_rank(self.rank - 1)
        else:
            self.lose_life()

    def lose_life(self):
        self.lives -= 1
        if self.lives > 0:
            self.set_rank(1)
            self.reset_item_effects()
            self.level.start_current()
            sound.lose_life.play()

    def get_damage(self, damage: int):
        self.energy = max(0, self.energy - damage)
        if self.energy == 0:
            self.lose_rank()

    # List of default values to rescale the fire points of the ship depending on it's current size.
    @property
    def default_fire_points(self) -> list[tuple]:
        """Fire points on the original ship sprites."""
        match self.rank:
            case 1: return [(51.5,0)]
            case 2: return [(9,54),(53,0),(95,54)]
            case 3: return [(12,71),(23,49),(66.5,0),(109,49),(120,71)]

    @property
    def default_width(self) -> int:
        match self.rank:
            case 1: return 103
            case 2: return 106
            case 3: return 133

    @property
    def default_height(self) -> int:
        match self.rank:
            case 1: return 79
            case 2: return 146
            case 3: return 178

    @property
    def fire_points(self) -> list[Vector]:
        """Rescale where the ship shoots bullets respecting size changes of the ship."""
        return [self.pos + Vector(x * self.w / self.default_width, y * self.h / self.default_height) for (x,y) in self.default_fire_points]
        
    @property
    def bullet_sizes(self) -> list[int]:
        match self.rank:
            case 1: sizes = [1]
            case 2: sizes = [1,2,1]
            case 3: sizes = [1,2,3,2,1]
        return [min(3, size + self.bullets_buff) for size in sizes]

    def shoot_bullets(self):
        """Shoot bullets if there aren't too many ship bullets on the screen yet."""
        if len(self.level.ship_bullets) < SHIP.MAX_BULLETS * (2*self.rank-1) and self.status != "shield":
            doppler = self.vel.y # Take Doppler effect into account to calculate the bullets' speed.
            for fp, size in zip(self.fire_points, self.bullet_sizes):
                bullet = Bullet.from_size(size)
                bullet.spawn(center = fp)
                bullet.vel.y -= doppler
                self.level.ship_bullets.add(bullet)
                self.level.bullets.add(bullet)
            bullet.play_firing_sound()

    def control(self, keys):
        """Control the ship's direction and shield according to the current state of the keyboard."""
        if keys[KEY.SHIELD]:
            if self.status != "shield" and self.shield_time > 0:
                self.activate_shield()
                self.vel = Vector(0,0)
        else:
            if self.status == "shield":
                self.deactivate_shield()
            direction = Vector(keys[KEY.RIGHT]-keys[KEY.LEFT], keys[KEY.DOWN]-keys[KEY.UP])
            self.vel = self.speed_factor * SHIP.SPEED[self.rank] * normalize(direction)
            if self.status == "inverse_controls":
                self.vel *= -1

    def update_graphic(self):
        """Upon changes of status or size, the ship's graphic must be updated."""
        letter = {"normal":"a", "inverse_controls":"g", "shield":"h", "magnetic":"e"}[self.status]
        self.graphic = GraphicData(path = f"images/ship/{letter}-{self.rank}.png", scaling_width = SHIP.WIDTH[self.rank])
        self.change_image(self.graphic.image.scale_by(self.size_factor))

    def collect_item(self, item: Item):
        """Trigger item effects and sound. Timers are set for temporary effects."""
        item.play_collecting_sound()
        match item.template.name:
            case "bullets_buff": self.bullets_buff += 1
            case "hp_plus": self.energy = min(self.max_energy, self.energy + item.template.effect)
            case "invert_controls":
                if self.status == "inverse_controls":
                    self.status = "normal"
                    self.controls_timer.pause()
                else:
                    self.status = "inverse_controls"
                    self.controls_timer.set_alarm(item.duration_ms, cyclic = False)
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
                    self.score_buff_timer.set_alarm(item.duration_ms, cyclic = False)
                self.score_factor *= item.template.effect
            case "shield":
                self.shield_timer.alarm_time += min(1000 * item.template.effect, 1000 * SHIP.MAX_SHIELD_DURATION - self.shield_time)
                self.shield_timer.total_timer = 0
            case "ship_buff": self.gain_rank()
            case "size_minus":
                if self.size_factor * item.template.effect >= 0.3:
                    self.size_factor *= item.template.effect
                    self.update_graphic()
                    if self.size_factor != 1:
                        self.size_change_timer.set_alarm(item.duration_ms, cyclic = False)
            case "size_plus":
                if self.size_factor * item.template.effect <= 1/0.3:
                    self.size_factor *= item.template.effect
                    self.update_graphic()
                    if self.size_factor != 1:
                        self.size_change_timer.set_alarm(item.duration_ms, cyclic = False)
            case "speed_buff":
                if self.speed_factor * SHIP.SPEED[self.rank] * item.template.effect < BULLET.BULLET1.speed:
                    self.speed_factor *= item.template.effect
                    if self.speed_factor != 1:
                        self.speed_change_timer.set_alarm(item.duration_ms, cyclic = False)
            case "speed_nerf":
                self.speed_factor *= item.template.effect
                if self.speed_factor != 1:
                    self.speed_change_timer.set_alarm(item.duration_ms, cyclic = False)

    def activate_shield(self):
        """Activate shield if the player has remaining shield time left."""
        if self.shield_time > 0:
            self.shield_timer.resume()
            sound.shield.play()
            self.last_status, self.status = self.status, "shield"
            self.update_graphic()

    def deactivate_shield(self):
        """Method used to deactivate the shield when player releases the shield key or running out of shield time."""
        self.shield_timer.pause()
        if self.status == "shield":
            self.status = self.last_status
            self.update_graphic()

    def shoot_missile(self, pos: Vector):
        """Shoot missile to the given position on the screen."""
        if self.missiles > 0:
            self.missiles -= 1
            missile = Bullet(BULLET.MISSILE)
            missile.spawn(center=pos)
            self.level.bullets.add(missile)
            missile.play_firing_sound()

    def get_points(self, points: int):
        self.score += int(self.score_factor * points)

    def reset_item_effects(self):
        self.bullets_buff = 0
        self.speed_factor = 1
        self.magnet = False
        self.missiles = SHIP.STARTING_MISSILES
        self.score_factor = 1
        self.shield_timer.set_alarm(1000 * SHIP.SHIELD_STARTING_TIMER, cyclic = False)
        self.shield_timer.pause()
        self.size_factor = 1
        self.status = "normal"
        self.last_status = "normal"

    def update(self, dt: int):
        """Update the ship's position, shield and item timers after dt passed ms"""
        for timer in self.timers:
            timer.update(dt)
        if self.shield_timer.check_alarm():
            self.deactivate_shield()
        if self.score_buff_timer.check_alarm():
            self.score_factor = 1
        if self.speed_change_timer.check_alarm():
            self.speed_factor = 1
        if self.size_change_timer.check_alarm():
            self.size_factor = 1
            self.update_graphic()
        if self.controls_timer.check_alarm():
            self.status = "normal"
            self.update_graphic()
        super().update(dt)