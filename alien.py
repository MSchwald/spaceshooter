import pygame, settings, sound
from image import Image
from sprite import Sprite
from bullet import Bullet
from display import Display
from item import Item
from random import random, choice, randint, sample
from math import pi, sqrt, sin, cos
from math import hypot
from settings import AlienType, BIG_ASTEROID, SMALL_ASTEROID, PURPLE, UFO, BLOB, GREEN_BULLET, BLUBBER

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

    def __init__(self, type: AlienType, level, cycle_time=None, random_cycle_time=(800,1500),
                grid=None, center=None, x=0, y=0, v=None, direction=None, constraints=None, boundary_behaviour="reflect",
                energy=None):
        #level: needs access to the level object from the game file
        #cycle_time: Alien periodically does actions after given time (in ms)
        #random_cycle_time is a tuple of floats: cycle times vary randomly between given lower and upper bound (in ms)
        v = v if v is not None else type.speed
        constraints = constraints or pygame.Rect(0, 0, Display.screen_width, Display.screen_height)
        self.energy = energy or type.energy
        #Load frames and images
        if type.animation_type:
            image = None
            frames = Image.load(f"images/alien/{type.name}", colorkey=type.colorkey)
            animation_type, fps = type.animation_type, type.fps
        else:
            frames, animation_type, fps = None, None, None
            if type.name == "blob":
                image = Image.blob[self.energy-1]
            else:
                image = Image.load(f'images/alien/{type.name}.png',colorkey=type.colorkey)
                
        super().__init__(image=image,
                            grid=grid, center=center, x=x, y=y, v=v, direction=direction,
                            constraints=constraints, boundary_behaviour=boundary_behaviour,
                            animation_type=animation_type, frames=frames, fps=fps)
        self.type = type
        self.level = level
        self.points = type.points
        self.cycle_time = cycle_time
        self.random_cycle_time = random_cycle_time
        if random_cycle_time:
            self.cycle_time = randint(random_cycle_time[0],random_cycle_time[1])
        if self.cycle_time:
            self.action_timer = 0
        #blobs gravitate towards the place they got split the last time
        if type.name == "blob":
            self.parent_center = None

    def play_spawing_sound(self):
        match self.type.name:
            case "purple": sound.alien_spawn.play()
            case "blob": sound.blob_spawns.play()

    @property
    def mass(self):
        """mass of an enemy, relevant for collisions between asteroids and blobs"""
        match self.type.name:
            case "blob": return self.energy
            case "big_asteroid" | "small_asteroid":
                return (self.w/Display.grid_width)**3
            case _:
                return None

    def update(self, dt):
        #asteroids can collide (elastic collision of 2d balls)
        if self.type.name in ["big_asteroid","small_asteroid"]:
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
                    f = 2/(self.mass+ast.mass)*dvn
                    f1 = -ast.mass*f
                    f2 = self.mass*f
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
            if self.cycle_time and not self.timer_on_hold and self.level.status != "start":
                self.action_timer += dt
                if self.action_timer >= self.cycle_time:
                    self.action_timer -= self.cycle_time
                    if self.random_cycle_time:
                        self.cycle_time = randint(self.random_cycle_time[0],self.random_cycle_time[1])
                    self.do_action()
            #blobs gravitate towards their parent center
            if self.type.name == "blob" and self.parent_center:
                x1,y1 = self.rect.center
                x2,y2 = self.parent_center
                n = normalize((x2-x1,y2-y1))
                vr = self.vx*n[0]+self.vy*n[1]
                ar = -BLOB.acceleration*(vr-self.splitting_speed)*abs(vr+self.splitting_speed)
                self.a = (ar*n[0],ar*n[1])
            #timer, movement and animation get handled in the Sprite class
            super().update(dt)

    def do_action(self):
        match self.type.name:
            case "purple": self.shoot(GREEN_BULLET)
            case "ufo": self.throw_alien(PURPLE)
            case "blob": self.shoot(BLUBBER, size=self.energy)

    # types of alien actions
    def shoot(self, bullet_type, size=None):
        bullet = Bullet(bullet_type,size=size,center=self.rect.midbottom)
        self.level.bullets.add(bullet)
        bullet.play_firing_sound()

    def throw_alien(self, alien_type):
        self.level.aliens.add(Alien(PURPLE,self.level,center=self.rect.midbottom, direction=(2*random()-1,1)))

    def get_damage(self, damage):
        if self.type.name == "big_asteroid":
            self.energy = 0
        elif self.type.name == "blob":
            self.kill()
        else:
            self.energy = max(self.energy-damage,0)
            if self.energy > 0 and self.type.name not in ["big_asteroid", "small_asteroid"]:
                {"purple": sound.enemy_hit, "ufo": sound.metal_hit}[self.type.name].play()
            else:
                self.kill()

    def split(self, new_type: AlienType, amount):
        if self.direction==(0,0):
            phi = random()
            w=(cos(2*pi*phi),sin(2*pi*phi))
        else:
            w=(self.direction[0]/self.norm, self.direction[1]/self.norm)
        if new_type.name == "blob":
            #blobs split into smaller blobs with integer mass
            m = self.mass // amount
            diff = self.mass - amount * m
            masses = [m + 1 if i < diff else m for i in sample(range(amount), amount)]
        pieces = []
        for i in range(amount):
            if new_type.name == "blob":
                if masses[i] == 0:
                    continue
                speed_factor = masses[i]**(-1/2)
            else:
                speed_factor = 1
            phi_i=(2*i+1)*pi/amount
            dir_i = (self.vx+new_type.speed*speed_factor*(w[0]*cos(phi_i)-w[1]*sin(phi_i)),
                self.vy+new_type.speed*speed_factor*(w[0]*sin(phi_i)+w[1]*cos(phi_i)))
            energy = masses[i] if new_type.name == "blob" else None
            pieces.append(Alien(new_type, self.level, energy=energy, direction=dir_i, v=norm(dir_i), center=self.rect.center,
                constraints=self.constraints, boundary_behaviour=self.boundary_behaviour))
        return(pieces)

    @classmethod
    def merge(cls, blob1, blob2):
        """merges two blobs, but could be generalized to other aliens"""
        x1,y1 = blob1.rect.center
        x2,y2 = blob2.rect.center
        vx1, vy1 = blob1.vx, blob1.vy
        vx2, vy2 = blob2.vx, blob2.vy
        m1, m2 = blob1.mass, blob2.mass
        # blobs merge at their center of gravity
        new_x = (m1 * x1 + m2 * x2) / (m1 + m2)
        new_y = (m1 * y1 + m2 * y2) / (m1 + m2)
        new_center = (new_x, new_y)
        # Conservation of momentum (inelastic collision)
        vx_new = (m1 * vx1 + m2 * vx2) / (m1 + m2)
        vy_new = (m1 * vy1 + m2 * vy2) / (m1 + m2)
        new_v = hypot(vx_new, vy_new)
        if new_v != 0:
            new_dir = (vx_new / new_v, vy_new / new_v)
        else:
            new_dir = (0, 0)
        return Alien(BLOB, blob1.level, energy=blob1.energy+blob2.energy,center=new_center,direction=new_dir,v=new_v)

    def kill(self):
        """removes an enemy, triggers splitting for asteroids and blobs""" 
        if self.energy <= 0:
            {"big_asteroid": sound.asteroid, "small_asteroid": sound.small_asteroid, "purple": sound.alienblob, "ufo":sound.alienblob, "blob":sound.alienblob}[self.type.name].play()
            self.level.ship.get_points(self.points)
            if random() <= settings.Item.PROBABILITY:
                self.level.items.add(Item(choice(settings.Item.TYPES), self.level, center=self.rect.center))
        if self.type.name == "big_asteroid":
            # big asteroids split into smaller asteroids when hit
            for piece in self.split(SMALL_ASTEROID, self.type.pieces):
                self.level.asteroids.add(piece)
        if self.type.name == "blob":
            if self.energy > 1:
                sound.slime_hit.play()
                for blob in self.split(BLOB, self.type.pieces):
                    blob.splitting_speed = blob.v # needed later to calculate the gravitation towards the parent center
                    blob.parent_center = self.rect.center
                    self.level.aliens.add(blob)
                    self.level.blobs.add(blob)
            elif self.energy == 1:
                sound.alienblob.play()
                self.level.ship.get_points(self.points)
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