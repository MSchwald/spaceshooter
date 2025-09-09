import pygame
from pygame.locals import *
import settings
import image
from image import Image
from sprite import Sprite
from bullet import Bullet
from random import random,choice,randint
import sound
from item import Item
from math import pi, sqrt, sin, cos
from math import hypot


def norm(v):
    return hypot(v[0],v[1])
def norm2(v):
    return v[0]*v[0]+v[1]*v[1]
def normalize(v):
    norm_v = norm(v)
    if norm_v == 0:
        return (0,0)
    return (v[0]/norm_v,v[1]/norm_v)

class Alien(Sprite):
    """A class to manage the enemies"""

    def __init__(self, type, level, cycle_time=None, random_cycle_time=(500,1000),
                grid=None, center=None, x=0, y=0, v=None, direction=None, constraints=pygame.Rect(settings.alien_constraints), boundary_behaviour="reflect",
                scaling_width=settings.grid_width):
        #level: needs access to the level object from the game file
        #cycle_time: Alien periodically does actions after given time (in ms)
        #random_cycle_time is a tuple of floats: cycle times vary randomly between given lower and upper bound (in ms)
        
        #Load frames and images
        if type in ["big_asteroid", "small_asteroid"]:
            super().__init__(frames = [Image.load(f"images/{type}/{str(n+1)}.png", scaling_width=settings.alien_width[type]) for n in range(14)], animation_type="loop", fps=10, grid=grid, center=center, x=x, y=y, v=settings.alien_speed[type], direction=direction,
                         constraints=constraints, boundary_behaviour=boundary_behaviour)
            #mass is so far only relevant for collisions between the asteroids
            self.m = (self.w/settings.grid_width)**3
        else:
            super().__init__(Image.load(f'images/alien/{str(type)}.png',colorkey=settings.alien_colorkey[type], scaling_width=settings.alien_width[type]), grid=grid, center=center, x=x, y=y, v=settings.alien_speed[type], direction=direction,
                             constraints=constraints, boundary_behaviour=boundary_behaviour)
        if type == "purple":
            sound.alien_spawn.play()
        
        self.type = type
        self.level = level
        self.energy = settings.alien_energy[type]
        self.points = settings.alien_points[type]
        self.cycle_time = cycle_time
        self.random_cycle_time = random_cycle_time
        if random_cycle_time:
            self.cycle_time = randint(random_cycle_time[0],random_cycle_time[1])
        if self.cycle_time:
            self.action_timer = 0

    def update(self, dt):
        #asteroids can collide (elastic collision of balls)
        if self.type in ["big_asteroid","small_asteroid"]:
            for ast in self.level.asteroids:
                dp = (self.rect.center[0]-ast.rect.center[0],self.rect.center[1]-ast.rect.center[1])
                n2dp = norm2(dp)
                dv = (self.vx-ast.vx,self.vy-ast.vy)
                d2 =(self.w+ast.w)**2/4
                n2dv = norm2(dv)
                dpdv = dp[0]*dv[0]+dp[1]*dv[1]
                if n2dv>1e-8 and n2dp < d2 and dpdv < 0:
                    t = (-dpdv-sqrt(dpdv**2-n2dv*(n2dp-d2)))/n2dv
                    super().update_position(t)
                    Sprite.update_position(ast,t)
                    n = normalize((self.rect.center[0]-ast.rect.center[0],self.rect.center[1]-ast.rect.center[1]))
                    dv = (self.vx-ast.vx,self.vy-ast.vy)
                    dvn = dv[0]*n[0]+dv[1]*n[1]
                    f = 2/(self.m+ast.m)*dvn
                    f1 = -ast.m*f
                    f2 = self.m*f
                    self.direction = (self.vx+f1*n[0],self.vy+f1*n[1])
                    ast.direction = (ast.vx+f2*n[0],ast.vy+f2*n[1])
                    self.v = norm(self.direction)
                    ast.v = norm(ast.direction)
                    super().update_position(-t)
                    Sprite.update_position(ast,-t)
            super().update(dt)

        # aliens move without collisions
        else:
            #checks if it is time for the alien to do an action
            if self.cycle_time and not self.timer_on_hold:
                self.action_timer += dt
                if self.action_timer >= self.cycle_time:
                    self.action_timer -= self.cycle_time
                    if self.random_cycle_time:
                        self.cycle_time = randint(self.random_cycle_time[0],self.random_cycle_time[1])
                    self.do_action()
            #timer, movement and animation get handled in the Sprite class
            super().update(dt)

    def do_action(self):
        if self.type == "purple":
            #purple aliens shoot green bullets
            self.shoot("g")
            #self.level.alien_random_entrance("big_asteroid")

        elif self.type == "ufo":
            #ufo aliens throw purple aliens
            choice([lambda: self.shoot("g"), lambda: self.throw_alien("purple")])()

    # types of alien actions

    def shoot(self, bullet_type):
        self.level.bullets.add(Bullet(bullet_type,center=self.rect.midbottom))

    def throw_alien(self, alien_type):
        self.level.aliens.add(Alien("purple",self.level,center=self.rect.midbottom, direction=(2*random()-1,1)))

    def get_damage(self, damage):
        if self.type == "big_asteroid":
            self.energy = 0
        self.energy -= damage
        if self.energy > 0 and self.type not in ["big_asteroid", "small_asteroid"]:
            {"purple": sound.enemy_hit,"ufo": sound.metal_hit}[self.type].play()
        else:
            self.kill()

    def kill(self):
        if self.energy <= 0:
            {"big_asteroid": sound.asteroid, "small_asteroid": sound.small_asteroid, "purple": sound.alienblob, "ufo":sound.alienblob}[self.type].play()
            self.level.ship.get_points(self.points)
            if random() <= settings.item_probability:
                self.level.items.add(Item(choice(settings.item_types), self.level, center=self.rect.center))
        if self.type == "big_asteroid":
                # big asteroids split into smaller asteroids when hit
                if self.direction==(0,0):
                    phi = random()
                    w=(cos(2*pi*phi),sin(2*pi*phi))
                else:
                    w=(self.direction[0]/self.norm,self.direction[1]/self.norm)
                for i in range(settings.asteroid_pieces):
                    phi=(2*i+1)*pi/settings.asteroid_pieces
                    new_dir = (self.vx+settings.alien_speed["small_asteroid"]*(w[0]*cos(phi)-w[1]*sin(phi)), self.vy+settings.alien_speed["small_asteroid"]*(w[0]*sin(phi)+w[1]*cos(phi)))
                    self.level.asteroids.add(Alien("small_asteroid", self.level, direction=new_dir, v=norm(new_dir), center=self.rect.center, constraints=self.constraints, boundary_behaviour=self.boundary_behaviour))
        super().kill()

    def reflect(self):
        sound.shield.stop()
        sound.shield_reflect.play()
        super().reflect(flip_x=False, flip_y=False)