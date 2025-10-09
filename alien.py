from __future__ import annotations
import pygame, settings, sound
from image import Image, GraphicData
from sprite import Sprite
from bullet import Bullet
from display import Display
from item import Item
from timer import ActionTimer
from random import random, choice, randint, sample
from math import pi, sqrt, sin, cos
from settings import AlienTemplate, ALIEN, BULLET, ITEM
from physics import Vector, norm, normalize, random_direction, turn_by_angle, inelastic_collision, ball_collision_data

class Alien(Sprite):
    """Manage sprites, spawning and actions of enemies"""

    def __init__(self, template: AlienTemplate,
                level: Level,
                energy: int | None = None,
                speed: float | None = None,
                direction: Vector | None = None,
                pos: Vector | None = None,
                vel: Vector | None = None,
                acc: Vector = Vector(0, 0),
                constraints: pygame.Rect | None = None,
                boundary_behaviour: str | None = "reflect"):
        # energy and speed allow overwriting their standard settings for given template        
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
        if template.name == "blob":
            self.parent_center = None
            graphic = GraphicData(image = Image.blob[self.energy-1])
        else:
            graphic = GraphicData(path = f"images/alien/{template.name}", scaling_width = template.width, colorkey = template.colorkey,
                    animation_type = template.animation_type, fps = template.fps)
                
        super().__init__(graphic = graphic, pos = pos, vel = vel, acc = acc,
                    constraints = constraints, boundary_behaviour = boundary_behaviour)
            
    def spawn(self, **kwargs):
        if self.level.number != 0:
            self.play_spawing_sound()
        super().spawn(**kwargs)

    def play_spawing_sound(self):
        match self.template.name:
            case "purple": sound.alien_spawn.play()
            case "blob": sound.blob_spawns.play()

    @property
    def mass(self) -> int | None:
        """mass of an enemy, relevant for collisions between asteroids and blobs"""
        match self.template.name:
            case "blob": return self.energy
            case "big_asteroid" | "small_asteroid":
                """make mass independent of display settings"""
                return (self.w / Display.grid_width) ** 3
            case _:
                return None

    def update(self, dt: int):
        super().update(dt)
        self.action_timer.update(dt)
        while self.level.status != "start" and self.action_timer.check_alarm():
            self.do_action()

        #asteroids collide elastically like 3d balls
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
                #blobs gravitate towards their parent center where they split last
                if self.parent_center is None:
                    return
                n = normalize(self.parent_center - self.center)
                vr = self.vel * n
                self.acc = - ALIEN.BLOB.acc * (vr - self.splitting_speed) * abs(vr + self.splitting_speed) * n            

    def do_action(self):
        match self.template.name:
            case "purple": self.shoot(BULLET.GREEN)
            case "ufo": self.throw_alien(ALIEN.PURPLE)
            case "blob": self.shoot(BULLET.BLUBBER, size=self.energy)

    # templates of alien actions
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
                {"purple": sound.enemy_hit, "ufo": sound.metal_hit}[self.template.name].play()
            else:
                self.kill()

    def split(self, piece_template: AlienTemplate, amount: int) -> list[Alien]:
        if self.speed == 0:
            w = random_direction()
        else:
            w = normalize(self.vel)
        if piece_template.name == "blob":
            #blobs split into smaller blobs with integer mass
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
        """merges two blobs, but could be generalized to other aliens"""
        p1, p2 = blob1.center, blob2.center
        v1, v2 = blob1.vel, blob2.vel
        m1, m2 = blob1.mass, blob2.mass
        new_center, new_vel = inelastic_collision(p1, p2, v1, v2, m1, m2)
        blob = Alien(ALIEN.BLOB, blob1.level, energy = blob1.energy + blob2.energy, vel = new_vel)
        Sprite.spawn(blob, center = new_center)
        return blob

    def kill(self):
        """removes an enemy, triggers splitting for asteroids and blobs""" 
        if self.energy <= 0:
            {"big_asteroid": sound.asteroid, "small_asteroid": sound.small_asteroid, "purple": sound.alienblob, "ufo":sound.alienblob, "blob":sound.alienblob}[self.template.name].play()
            self.level.ship.get_points(self.template.points)
            if random() <= ITEM.PROBABILITY:
                item = Item(choice(ITEM.LIST), self.level)
                item.spawn(center = self.center)
                self.level.items.add(item)
        if self.template.name == "big_asteroid":
            # big asteroids split into smaller asteroids when hit
            for piece in self.split(ALIEN.SMALL_ASTEROID, self.template.pieces):
                self.level.asteroids.add(piece)
        if self.template.name == "blob":
            if self.energy > 1:
                sound.slime_hit.play()
                for blob in self.split(ALIEN.BLOB, self.template.pieces):
                    blob.splitting_speed = blob.speed # needed later to calculate the gravitation towards the parent center
                    blob.parent_center = self.center
                    self.level.aliens.add(blob)
                    self.level.blobs.add(blob)
            elif self.energy == 1:
                sound.alienblob.play()
                self.level.ship.get_points(self.template.points)
                self.hard_kill()
        super().kill()

    def hard_kill(self):
        """removes an enemy without further splitting"""
        self.level.aliens.remove(self)
        self.level.blobs.remove(self)
        super(Alien, self).kill()

    def reflect(self):
        if self.level.status != "start":
            sound.shield.stop()
            sound.shield_reflect.play()
        super().reflect(flip_x=False, flip_y=False)