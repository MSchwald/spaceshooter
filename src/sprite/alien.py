from __future__ import annotations
import pygame
from sound import Sound
from settings import AlienTemplate, ALIEN, BULLET, ITEM, LEVEL_STATUS
from display import Display
from image import Image, GraphicData
from sprite import Sprite, BOUNDARY
from bullet import Bullet
from item import Item
from timer import ActionTimer
from random import random, choice, randint, sample
from math import pi, sqrt, sin, cos
from physics import Vector, norm, normalize, random_direction, turn_by_angle, inelastic_collision, ball_collision_data

class Alien(Sprite):
    """Manage sprites, spawning and actions of enemies."""

    def __init__(self, template: AlienTemplate,
                level: Level,
                energy: int | None = None,
                speed: float | None = None,
                direction: Vector | None = None,
                pos: Vector | None = None,
                vel: Vector | None = None,
                acc: Vector = Vector(0, 0),
                constraints: pygame.Rect | None = None,
                boundary_behaviour: str | None = BOUNDARY.REFLECT):
        """energy, speed: allow for overwriting their default settings for given template."""       
        self.template = template
        self.level = level
        self.energy = energy or template.energy
        speed = speed or template.speed
        if vel is None:
            direction = direction or random_direction()
            vel = speed * direction
        constraints = constraints or Display.screen_rect
        self.action_timer = ActionTimer(template.alarm_min, template.alarm_max, cyclic = True)

        # Load alien graphics
        graphic = GraphicData(path = f"images/alien/{template.name}", scaling_width = template.width, colorkey = template.colorkey,
                    animation_type = template.animation_type, fps = template.fps)
        super().__init__(graphic = graphic, pos = pos, vel = vel, acc = acc,
                    constraints = constraints, boundary_behaviour = boundary_behaviour)
        if template.name == "blob":
            self.parent_center = None
            self.update_blob_image()

    def update_blob_image(self):
        """A blob's image and size depend on its energy."""
        if self.template.name != "blob":
            return
        if self.energy < ALIEN.BLOB.energy // 8:
            self.frame_index = 2
        elif self.energy <= ALIEN.BLOB.energy // 4:
            self.frame_index = 1
        else:
            self.frame_index = 0
        scaling_factor = (ALIEN.BLOB.energy / self.energy) ** (-1/3)
        self.graphic.image = self.graphic.frames[self.frame_index].scale_by(scaling_factor)

    def spawn(self, **kwargs):
        """Place an initiated alien and play it's spawning sound"""
        if self.level.number != 0:
            self.play_spawing_sound()
        super().spawn(**kwargs)

    def play_spawing_sound(self):
        match self.template.name:
            case "purple": Sound.alien_spawn.play()
            case "blob": Sound.blob_spawns.play()

    @property
    def mass(self) -> int | None:
        """Mass of an enemy, relevant for collisions between asteroids and blobs."""
        match self.template.name:
            case "blob": return self.energy
            case "big_asteroid" | "small_asteroid":
                # Make mass independent of display settings.
                return (self.w / Display.grid_width) ** 3
            case _:
                # Not implemented.
                return None

    def update(self, dt: int):
        """Calculate the state of the alien after dt passed ms"""
        super().update(dt)
        self.action_timer.update(dt)
        while self.level.status != LEVEL_STATUS.START and self.action_timer.check_alarm():
            self.do_action()

        # Asteroids collide elastically like 3d balls.
        match self.template.name:
            case "big_asteroid" | "small_asteroid":
                for ast in self.level.asteroids:
                    if ast is self:
                        continue
                    ball1, ball2, m1, m2 = self.ball, ast.ball, self.mass, ast.mass
                    collision_time, new_v1, new_v2 = ball_collision_data(ball1, ball2, m1, m2)
                    if collision_time is None:
                        continue
                    super().update_pos(collision_time)
                    Sprite.update_pos(ast, collision_time)
                    self.vel, ast.vel = new_v1, new_v2                  
                    super().update_pos(-collision_time)
                    Sprite.update_pos(ast, -collision_time)
            case "blob":
                # Blobs gravitate towards their parent center where they split last.
                if self.parent_center is None:
                    return
                n = normalize(self.parent_center - self.center)
                vr = self.vel * n
                self.acc = - ALIEN.BLOB.acc * (vr - self.splitting_speed) * abs(vr + self.splitting_speed) * n            

    def do_action(self):
        """Triggers an alien's specific action."""
        match self.template.name:
            case "purple": self.shoot(BULLET.GREEN)
            case "ufo": self.throw_alien(ALIEN.PURPLE)
            case "blob": self.shoot(BULLET.BLUBBER, size=self.energy)

    # Templates of alien actions
    def shoot(self, bullet_template: BulletTemplate, size: int | None = None):
        bullet = Bullet(bullet_template, size=size)
        bullet.spawn(center = self.midbottom)
        self.level.bullets.add(bullet)
        bullet.play_firing_sound()

    def throw_alien(self, alien_template: AlienTemplate = ALIEN.PURPLE):
        alien = Alien(alien_template, self.level, direction = Vector(self.vel.x, -1))
        alien.spawn(center = self.center)
        self.level.aliens.add(alien)

    def get_damage(self, damage: int):
        if self.template.name == "big_asteroid":
            self.energy = 0
        elif self.template.name == "blob":
            self.kill()
        else:
            self.energy = max(self.energy - damage, 0)
            if self.energy > 0 and self.template.name not in ("big_asteroid", "small_asteroid"):
                {"purple": Sound.enemy_hit, "ufo": Sound.metal_hit}[self.template.name].play()
            else:
                self.kill()

    def split(self, piece_template: AlienTemplate, amount: int) -> list[Alien]:
        """Splits an Alien preserving the total impuls. Used for asteroids and blobs."""
        if self.speed == 0:
            w = random_direction()
        else:
            w = normalize(self.vel)
        if piece_template.name == "blob":
            # Blobs split into smaller blobs with integer mass.
            m = self.mass // amount
            diff = self.mass - amount * m
            masses = [m + 1 if i < diff else m for i in sample(range(amount), amount)]
        pieces = []
        for i in range(amount):
            if piece_template.name == "blob":
                if masses[i] == 0:
                    continue
                speed_factor = masses[i] ** (-1/2)
            else:
                speed_factor = 1
            phi_i = (2*i+1) * pi / amount
            vel_i = self.vel + speed_factor * piece_template.speed * turn_by_angle(w, phi_i)
            energy = masses[i] if piece_template.name == "blob" else None
            piece = Alien(piece_template, self.level, energy=energy, vel=vel_i,
                constraints=self.constraints, boundary_behaviour=self.boundary_behaviour)
            Sprite.spawn(piece, center = self.center)
            pieces.append(piece)
        return pieces

    @classmethod
    def merge(cls, blob1: Alien, blob2: Alien):
        """Merge two blobs. Can also be used for other aliens if their masses are implemented."""
        p1, p2 = blob1.center, blob2.center
        v1, v2 = blob1.vel, blob2.vel
        m1, m2 = blob1.mass, blob2.mass
        new_center, new_vel = inelastic_collision(p1, p2, v1, v2, m1, m2)
        blob = Alien(ALIEN.BLOB, blob1.level, energy = blob1.energy + blob2.energy, vel = new_vel)
        Sprite.spawn(blob, center = new_center)
        return blob

    def kill(self):
        """Removes an enemy, trigger splitting for asteroids and blobs.""" 
        if self.energy <= 0:
            {"big_asteroid": Sound.asteroid, "small_asteroid": Sound.small_asteroid, "purple": Sound.alienblob, "ufo":Sound.alienblob, "blob":Sound.alienblob}[self.template.name].play()
            self.level.ship.get_points(self.template.points)
            if random() <= ITEM.PROBABILITY:
                item = Item(choice(ITEM.LIST), self.level)
                item.spawn(center = self.center)
                self.level.items.add(item)
        if self.template.name == "big_asteroid":
            # Big asteroids split into smaller asteroids when hit.
            for piece in self.split(ALIEN.SMALL_ASTEROID, self.template.pieces):
                self.level.asteroids.add(piece)
        if self.template.name == "blob":
            if self.energy > 1:
                Sound.slime_hit.play()
                for blob in self.split(ALIEN.BLOB, self.template.pieces):
                    # The splitting data is saved for later to calculate
                    # the blob's gravitation towards it's parent center.
                    blob.splitting_speed = blob.speed 
                    blob.parent_center = self.center
                    self.level.aliens.add(blob)
                    self.level.blobs.add(blob)
            elif self.energy == 1:
                Sound.alienblob.play()
                self.level.ship.get_points(self.template.points)
                self.hard_kill()
        super().kill()

    def hard_kill(self):
        """Remove an enemy without triggering further splitting."""
        self.level.aliens.remove(self)
        self.level.blobs.remove(self)
        super(Alien, self).kill()

    def reflect(self):
        """Reflecting enemies with shield sound effects."""
        if self.level.status != LEVEL_STATUS.START:
            Sound.shield.stop()
            Sound.shield_reflect.play()
        super().reflect(flip_x = False, flip_y = False)