import pygame, settings
from pygame.locals import *
from ship import Ship
from alien import Alien
import sound
from random import random
from math import hypot

#placement of enemies in an 16x9-grid
lst = {1: [(4, 1, "big_asteroid", (1,0)), (6, 1, "big_asteroid", (0,1)), (9, 5, "big_asteroid", (0,1)), (11, 1, "big_asteroid", "random"), (2, 1, "big_asteroid", (1,0)), (13, 1, "big_asteroid", (1,0))],
2: [(1, 1, "purple", (1, 1)), (3, 1, "purple", (1, 1)), (5, 1, "purple", (1, 1))],
3: [(1, 1, "ufo", (2, 0))],
4: [(3, 3, "blob", "random")]#,(6, 1, "blob", "random"),(9, 1, "blob", "random"),(12, 1, "blob", "random")]
}
max_level = max(lst.keys())


class Level:
    """A class to manage the game levels"""

    def __init__(self, number):
        # Initializes the Ship
        self.ship = Ship(self)
        # Initializes level number and empty sprite groups
        self.number = number
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
        else:
            if self.number == 1 and not self.asteroids:
                sound.start.play()
                return "solved"
            elif self.number in [2,3] and not self.aliens:
                sound.start.play()
                return "solved"
            elif self.number == 4 and not self.blobs:
                pygame.mixer.stop()
                sound.start.play()
                return "solved"
            elif self.number == 5 and self.timer > 60000:
                pygame.mixer.stop()
                sound.game_won.play()
                return "game won"
            else:
                return "running"

    def start(self):
        self.ship.reset_position()
        # Resets the Groups of bullets and enemies
        self.ship_bullets.empty()
        self.bullets.empty()
        self.asteroids.empty()
        self.aliens.empty()
        self.blobs.empty()
        for (x, y, type, direction) in lst[self.number]:
                if type in ["big_asteroid","small_asteroid"]:
                    self.asteroids.add(Alien(type=type, level=self, grid=(x,y), direction=direction))
                else:
                    alien = Alien(type=type, level=self, v=0, grid=(x,y), direction=direction)
                    if type == "blob": #blobs are also aliens
                        self.blobs.add(alien)
                    self.aliens.add(alien)


        self.timer = 0
        #if self.number == 4:

    def update(self, dt):
        self.timer += dt
        self.goal = {1: "Destroy all asteroids!", 2: "Defeat all aliens!", 3: "Defeat the ufo!", 4: "Defeat the blob!", 5: "Survive for a minute!"}[self.number]
        self.progress = {1: f"{len(self.asteroids)} left", 2: f"{len(self.aliens)} left", 3: f"health", 4:f"Blob energy: {sum([blob.energy for blob in self.blobs])}", 5: f"Timer: {int(60-self.timer/1000)}"}[self.number]
        # update all bullets, the ship and aliens
        for bullet in self.bullets:
            bullet.update(dt)
        self.ship.update(dt)
        for asteroid in self.asteroids:
            asteroid.update(dt)
        for alien in self.aliens:
            alien.update(dt)
        for item in self.items:
            item.update(dt)

        #collisions of blobs, they merge when not too big
        collisions = pygame.sprite.groupcollide(
            self.blobs, self.blobs, False, False, collided=pygame.sprite.collide_mask)
        merge_occured = False
        for blob1 in collisions.keys():
                if merge_occured:
                    break
                for blob2 in collisions[blob1][:]:
                    if blob2 is blob1 or blob1.energy+blob2.energy > settings.alien_energy["blob"]:
                        collisions[blob1].remove(blob2)
                    else:
                        x1,y1 = blob1.rect.center
                        x2,y2 = blob2.rect.center
                        vx1, vy1 = blob1.vx, blob1.vy
                        vx2, vy2 = blob2.vx, blob2.vy
                        dpdv = (x1-x2)*(vx1-vx2)+(y1-y2)*(vy1-vy2)
                        if dpdv >= 0:
                            collisions[blob1].remove(blob2)
                        else:
                            merge_occured = True
                            print("merge!",blob1.energy,blob2.energy )             
                            m1,m2 = blob1.m,blob2.m
                            # center of gravity
                            new_x = (m1 * x1 + m2 * x2) / (m1 + m2)
                            new_y = (m1 * y1 + m2 * y2) / (m1 + m2)
                            new_center = (new_x, new_y)
                            # Conservation of momentum
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
                            #print(self.energy,blob.energy,merged_blob.energy, len(self.level.blobs))
                            blob1.hard_kill()
                            blob2.hard_kill()

                            print([blob.energy for blob in self.blobs])
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
            else:
                self.aliens.add(alien)


