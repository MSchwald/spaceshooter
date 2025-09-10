import pygame, settings
from pygame.locals import *
from ship import Ship
from alien import Alien
import sound
from random import random
from math import hypot
from event import Event
from random import randint

#placement of enemies in an 16x9-grid
max_level = 5


class Level:
    """A class to manage the game levels"""

    def __init__(self, number):
        # Initializes the Ship
        self.ship = Ship(self)
        # Initializes level number and empty sprite groups
        self.number = number
        self.events = []
        self.ship_bullets = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.items = pygame.sprite.Group()
        self.asteroids = pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()
        self.blobs = pygame.sprite.Group()

    def status(self):
        if self.ship.lives <= 0:
            sound.game_over.play()
            return "game over"
        match self.number:
            case 1:
                if not self.asteroids:
                    sound.start.play()
                    return "solved"
            case 2:
                if not self.aliens:
                    sound.start.play()
                    return "solved"
            case 3:
                if self.ufo.energy == 0:
                    sound.start.play()
                    return "solved"
            case 4:
                if not self.blobs:
                    pygame.mixer.stop()
                    sound.start.play()
                    return "solved"
            case 5:
                if self.timer > 60000:
                    pygame.mixer.stop()
                    sound.game_won.play()
                    return "game won"
        return "running"

    def start(self):
        self.ship.reset_position()
        # Resets the Groups of bullets and enemies
        self.events=[]
        self.ship_bullets.empty()
        self.bullets.empty()
        self.asteroids.empty()
        self.aliens.empty()
        self.blobs.empty()
        match self.number:
            case 1:
                self.goal = "Destroy all asteroids!"
                for n in range(4,14,2):
                    self.asteroids.add(Alien(type="big_asteroid", level=self, grid=(n,1), direction="random"))
                for n in [2,14]:
                    self.asteroids.add(Alien(type="small_asteroid", level=self, grid=(n,1), direction="random"))
            case 2:
                self.goal = "Defeat all aliens!"
                self.events.append(Event("asteroid_hail", self, random_cycle_time=(800,1200)))
                for n in range(2,10,2):
                    self.aliens.add(Alien(type="purple", level=self, grid=(n,1), direction=(1,1), constraints=pygame.Rect([0,0,settings.screen_width,3*settings.grid_width])))
                for n in range(14,6,-2):
                    self.aliens.add(Alien(type="purple", level=self, grid=(n,5), direction=(-1,-1), constraints=pygame.Rect([0,3*settings.grid_width,settings.screen_width,3*settings.grid_width])))
            case 3:
                self.goal = "Defeat the ufo!"
                self.events.append(Event("asteroid_hail", self, random_cycle_time=(800,1000)))
                self.ufo = Alien(type="ufo", level=self, grid=(1,1), direction=(1,0))
                self.aliens.add(self.ufo)
                for n in [2,6]:
                    self.aliens.add(Alien(type="purple", level=self, grid=(n,1), direction=(1,0), constraints=pygame.Rect([0,0,settings.screen_width,3*settings.grid_width])))
                for n in [10,14]:
                    self.aliens.add(Alien(type="purple", level=self, grid=(n,5), direction=(-1,0), constraints=pygame.Rect([0,3*settings.grid_width,settings.screen_width,3*settings.grid_width]),random_cycle_time=(1200,2000)))
            case 4:
                self.goal = "Defeat the blob!"
                self.events.append(Event("asteroid_hail", self, random_cycle_time=(1000,1500)))            
                blob = Alien(type="blob", level=self, grid=(randint(1,14),1), direction="random")
                self.blobs.add(blob)
                self.aliens.add(blob)
            case 5:
                self.goal = "Survive for a minute!"
                self.events.append(Event("asteroid_hail", self, random_cycle_time=(800,1000)))            
        self.timer = 0


    def update(self, dt):
        self.timer += dt
        match self.number:
            case 1:                
                self.progress = f"{len(self.asteroids)} left"
            case 2:
                self.progress = f"{len(self.aliens)} left"
            case 3:
                self.progress = f"Ufo health: {self.ufo.energy}"
            case 4:
                self.progress = f"Blob energy: {sum([blob.energy for blob in self.blobs])}"
            case 5:
                self.progress = f"Timer: {int(60-self.timer/1000)}"
        # update all bullets, the ship and enemies
        for bullet in self.bullets:
            bullet.update(dt)
        self.ship.update(dt)
        for asteroid in self.asteroids:
            asteroid.update(dt)
        for alien in self.aliens:
            alien.update(dt)
        for item in self.items:
            item.update(dt)
        for event in self.events:
            event.update(dt)

        #collisions of blobs, they merge when not too big
        merge_occured = False
        for blob1 in self.blobs:
                if merge_occured:
                    break
                for blob2 in self.blobs:
                    if(
                        blob2 is not blob1
                        and blob1.energy+blob2.energy <= settings.alien_energy["blob"]
                        and pygame.sprite.collide_mask(blob1,blob2)
                    ):
                        x1,y1 = blob1.rect.center
                        x2,y2 = blob2.rect.center
                        vx1, vy1 = blob1.vx, blob1.vy
                        vx2, vy2 = blob2.vx, blob2.vy
                        dpdv = (x1-x2)*(vx1-vx2)+(y1-y2)*(vy1-vy2)
                        if dpdv < 0:
                            merge_occured = True            
                            m1,m2 = blob1.m,blob2.m
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
                            merged_blob = Alien("blob",self,energy=blob1.energy+blob2.energy,center=new_center,direction=new_dir,v=new_v)
                            self.aliens.add(merged_blob)
                            self.blobs.add(merged_blob)
                            blob1.hard_kill()
                            blob2.hard_kill()
                            sound.blob_merge.play()
                            break

    def next(self):
        if self.number < max_level:
            self.number += 1
            self.start()

    def restart(self):
        sound.start.play()
        self.number = settings.game_starting_level
        self.items.empty()
        self.ship.start_new_game()
        self.start()

    def alien_random_entrance(self, type, v=None, constraints = pygame.Rect(0, 0, settings.screen_width, settings.screen_height)):
            if v is None or v == 0:
                v = settings.alien_speed[type]
            alien = Alien(type, self, v=v, constraints=constraints, boundary_behaviour = "vanish")
            alien.constraints = pygame.Rect(constraints.x, constraints.y-alien.h, constraints.w, alien.h+constraints.h)
            alien.change_position(random()*(constraints.w-alien.w)+constraints.x, constraints.y-alien.h)
            alien.change_direction(random()*(constraints.w-alien.w)+constraints.x-alien.x, constraints.bottom-alien.rect.bottom)
            if type in ["big_asteroid","small_asteroid"]:
                self.asteroids.add(alien)
            elif type == "blob":
                sound.blob_spawns.play()
                self.blobs.add(alien)
                self.aliens.add(alien)
            else:
                self.aliens.add(alien)

    def start_asteroid_hail(self, cycle_time=None, random_cycle_time=(1000,2000),
                v=settings.alien_speed["big_asteroid"], constraints=pygame.Rect([0, 0, settings.screen_width, settings.screen_height]), boundary_behaviour="vanish"):
        self.events.add(Alien("asteroid_hail",self,cycle_time=cycle_time, random_cycle_time=random_cycle_time,
                v=v, constraints=constraints, boundary_behaviour=boundary_behaviour))

