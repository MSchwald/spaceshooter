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

w,N=settings.alien_width["blob"],settings.alien_energy["blob"]
big_blob_image = Image.load("images/alien/blob0.png", scaling_width=w)
medium_blob_image = Image.load("images/alien/blob1.png", scaling_width=w)
small_blob_image = Image.load("images/alien/blob2.png", scaling_width=w)
blob_images = [small_blob_image.scale_by((N/n)**(-1/3)) for n in range(1,N//8)]+[medium_blob_image.scale_by((N/n)**(-1/3)) for n in range(N//8,N//4+1)]+[big_blob_image.scale_by((N/n)**(-1/3)) for n in range(N//4+1, N+1)]

class Alien(Sprite):
    """A class to manage the enemies"""

    def __init__(self, type, level, cycle_time=None, random_cycle_time=(800,1500),
                grid=None, center=None, x=0, y=0, v=None, direction=None, constraints=pygame.Rect(settings.alien_constraints), boundary_behaviour="reflect",
                scaling_width=settings.grid_width, starting_frame=0, energy=None):
        #level: needs access to the level object from the game file
        #cycle_time: Alien periodically does actions after given time (in ms)
        #random_cycle_time is a tuple of floats: cycle times vary randomly between given lower and upper bound (in ms)
        if energy is None:
            energy = settings.alien_energy[type]
        if v is None:
            v = settings.alien_speed[type]
        #Load frames and images
        if type in ["big_asteroid", "small_asteroid"]:
            super().__init__(frames = [Image.load(f"images/{type}/{str(n+1)}.png", scaling_width=settings.alien_width[type]) for n in range(14)], animation_type="loop", fps=10, grid=grid, center=center, x=x, y=y, v=v, direction=direction,
                         constraints=constraints, boundary_behaviour=boundary_behaviour)
            #mass is so far only relevant for collisions between the asteroids and blobs
            self.m = (self.w/settings.grid_width)**3
        elif type == "blob":
            super().__init__(image=blob_images[energy-1],
                grid=grid, center=center, x=x, y=y, v=v, direction=direction,
                         constraints=constraints, boundary_behaviour="reflect")
            #mass of blobs is proportional to their energy points
            self.m = energy
            #blobs gravitate towards the place they got split the last time
            self.parent_center = None
            self.a = None

        else:
            super().__init__(Image.load(f'images/alien/{str(type)}.png',colorkey=settings.alien_colorkey[type], scaling_width=settings.alien_width[type]), grid=grid, center=center, x=x, y=y, v=v, direction=direction,
                             constraints=constraints, boundary_behaviour=boundary_behaviour)
        if type == "purple":
            sound.alien_spawn.play()
        self.type = type
        self.level = level
        self.points = settings.alien_points[type]
        self.cycle_time = cycle_time
        self.random_cycle_time = random_cycle_time
        if random_cycle_time:
            self.cycle_time = randint(random_cycle_time[0],random_cycle_time[1])
        if self.cycle_time:
            self.action_timer = 0
        self.energy = energy

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
            #blobs gravitate towards their parent center
            if self.type == "blob" and self.parent_center:
                x1,y1 = self.rect.center
                x2,y2 = self.parent_center
                n = normalize((x2-x1,y2-y1))
                vr = self.vx*n[0]+self.vy*n[1]
                ar = -0.2/32*(vr-self.u)*abs(vr+self.u)
                self.a = (ar*n[0],ar*n[1])
            #timer, movement and animation get handled in the Sprite class
            super().update(dt)

    def do_action(self):
        if self.type == "purple":
            #purple aliens shoot green bullets
            self.shoot("g")
            #self.level.alien_random_entrance("big_asteroid")

        elif self.type == "ufo":
            #ufo aliens throw purple aliens
            self.throw_alien("purple")

        if self.type == "blob":
            #blobs shoot bubbles
            self.shoot("blubber",size=self.energy)

    # types of alien actions
    def shoot(self, bullet_type, size=None):
        self.level.bullets.add(Bullet(bullet_type,size=size,center=self.rect.midbottom))

    def throw_alien(self, alien_type):
        self.level.aliens.add(Alien("purple",self.level,center=self.rect.midbottom, direction=(2*random()-1,1)))

    def get_damage(self, damage):
        if self.type == "big_asteroid":
            self.energy = 0
        elif self.type == "blob":
            self.kill()
        else:
            self.energy = max(self.energy-damage,0)
            if self.energy > 0 and self.type not in ["big_asteroid", "small_asteroid"]:
                {"purple": sound.enemy_hit,"ufo": sound.metal_hit}[self.type].play()
            else:
                self.kill()

    def kill(self):
        if self.energy <= 0:
            {"big_asteroid": sound.asteroid, "small_asteroid": sound.small_asteroid, "purple": sound.alienblob, "ufo":sound.alienblob, "blob":sound.alienblob}[self.type].play()
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
        if self.type == "blob":
            #blobs split into two smaller halfs
            # big asteroids split into smaller asteroids when hit
            if self.energy > 1:
                sound.slime_hit.play()
                if self.direction==(0,0):
                    phi = random()
                    w=(cos(2*pi*phi),sin(2*pi*phi))
                else:
                    w=(self.direction[0]/self.norm,self.direction[1]/self.norm)
                m1 = self.m//2
                m2 = self.m-m1
                phi=pi/2 #(2*i+1)*pi/2
                new_dir = (self.vx+settings.alien_speed["blob"]*m1**(-1/2)*(w[0]*cos(phi)-w[1]*sin(phi)), self.vy+settings.alien_speed["blob"]*m1**(-1/2)*(w[0]*sin(phi)+w[1]*cos(phi)))
                u = norm(new_dir)
                alien_1 = Alien("blob", self.level, energy=m1, direction=new_dir, v=u, center=self.rect.center, constraints=self.constraints, boundary_behaviour=self.boundary_behaviour)
                alien_1.u = u
                phi=3*pi/2
                new_dir = (self.vx+settings.alien_speed["blob"]*m2**(-1/2)*(w[0]*cos(phi)-w[1]*sin(phi)), self.vy+settings.alien_speed["blob"]*m2**(-1/2)*(w[0]*sin(phi)+w[1]*cos(phi)))
                u = norm(new_dir)
                alien_2 = Alien("blob", self.level, energy=m2,direction=new_dir, v=u, center=self.rect.center, constraints=self.constraints, boundary_behaviour=self.boundary_behaviour)
                alien_2.u = u
                self.level.aliens.add(alien_1,alien_2)
                self.level.blobs.add(alien_1,alien_2)
                alien_1.parent_center = self.rect.center
                alien_2.parent_center = self.rect.center
            elif self.energy == 1:
                sound.alienblob.play()
                self.level.ship.get_points(self.points)
                self.hard_kill()
        super().kill()

    def hard_kill(self):
        self.level.aliens.remove(self)
        self.level.blobs.remove(self)
        super(Alien, self).kill()

    def reflect(self):
        sound.shield.stop()
        sound.shield_reflect.play()
        super().reflect(flip_x=False, flip_y=False)