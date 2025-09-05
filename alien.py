import pygame
from pygame.locals import *
import settings
import image
from image import Image
from sprite import Sprite
from bullet import Bullet
from random import random,choice,randint
import sound
from math import pi
from item import Item

class Alien(Sprite):
    """A class to manage the enemies"""

    def __init__(self, type, level, cycle_time=None, random_cycle_time=(1000,2000),
                grid=None, center=None, x=0, y=0, direction=(0,0),
                scaling_width=settings.grid_width):
        #level: needs access to the level object from the game file
        #cycle_time: Alien periodically does actions after given time (in ms)
        #random_cycle_time is a tuple of floats: cycle times vary randomly between given lower and upper bound (in ms)
        
        #Load frames and images
        if type in ["big_asteroid", "small_asteroid"]:
            super().__init__(frames = [Image.load(f"images/{type}/{str(n+1)}.png", scaling_width=settings.alien_width[type]) for n in range(14)], animation_type="loop", fps=10, grid=grid, center=center, x=x, y=y, v=settings.alien_speed[type], direction=direction,
                         constraints=pygame.Rect(settings.alien_constraints), boundary_behaviour="reflect")
        else:
            super().__init__(Image.load(f'images/alien/{str(type)}.png',colorkey=settings.alien_colorkey[type], scaling_width=settings.alien_width[type]), grid=grid, center=center, x=x, y=y, v=settings.alien_speed[type], direction=direction,
                             constraints=pygame.Rect(settings.alien_constraints), boundary_behaviour="reflect")
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

    def update(self, dt, level):
        # checks if it is time for the alien to do an action
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

        elif self.type == "ufo":
            #ufo aliens throw purple aliens
            choice([lambda: self.shoot("g"), lambda: self.throw_alien("purple")])()

    # types of alien actions

    def shoot(self, bullet_type):
        self.level.bullets.add(Bullet(bullet_type,center=self.rect.midbottom))

    def throw_alien(self, alien_type):
        self.level.aliens.add(Alien("purple",self.level,center=self.rect.midbottom, direction=(2*random()-1,1)))

    def get_damage(self, damage):
        self.energy -= damage
        if self.energy > 0 and self.type not in ["big_asteroid", "small_asteroid"]:
            {"purple": sound.enemy_hit,"ufo": sound.metal_hit}[self.type].play()
        else:
            self.kill()

    def kill(self):
        {"big_asteroid": sound.asteroid, "small_asteroid": sound.small_asteroid, "purple": sound.alienblob, "ufo":sound.alienblob}[self.type].play()
        if self.type == "big_asteroid":
            # big asteroids split into four smaller asteroids when hit
            pieces = [Alien("small_asteroid", self.level, center=self.rect.center, direction=self.direction) for i in range(4)]
            for i in range(4):
                pieces[i].turn_direction((2*i+1)*pi/4)
                self.level.aliens.add(pieces[i])
        self.level.ship.get_points(self.points)
        if random() <= settings.item_probability:
            self.level.items.add(Item(choice(settings.item_types),center=self.rect.center))
        super().kill()

    def reflect(self):
        sound.shield.stop()
        sound.shield_reflect.play()
        super().reflect(flip_x=False, flip_y=False)