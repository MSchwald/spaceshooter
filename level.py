import pygame, settings, sound
from ship import Ship
from alien import Alien
from random import random, randint
from math import hypot
from event import Event
from sprite import Sprite
from image import Image
from statusbar import Statusbar
from display import Display

class Level:
    """A class to manage the game levels"""

    def __init__(self, number):
        '''Initializes all ingame objects and sprite groups'''
        self.ship = Ship(self)
        self.statusbar = Statusbar(self)
        self.crosshairs = Sprite(Image.load('images/bullet/aim.png'))
        Image.load_blob()
        self.number = number
        self.goals = ["Welcome!","Destroy all asteroids!","Defeat all aliens!","Defeat the ufo!","Defeat the blob!","Survive for a minute!"]
        self.max_level = len(self.goals)-1

        self.events = []
        # empty sprite groups
        self.ship_bullets = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.items = pygame.sprite.Group()
        self.asteroids = pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()
        self.blobs = pygame.sprite.Group()
        

    def blit(self, screen):
        """blit the current state of the level"""
        self.statusbar.blit(screen)
        for bullet in self.bullets:
            bullet.blit(screen)
        self.ship.blit(screen)

        for asteroid in self.asteroids:
            asteroid.blit(screen)
        for alien in self.aliens:
            alien.blit(screen)
        for item in self.items:
            item.blit(screen)

        self.crosshairs.blit(screen)

    def start(self):
        self.ship.reset_position()
        # Resets the Groups of bullets and enemies
        self.events=[]
        self.ship_bullets.empty()
        self.bullets.empty()
        self.asteroids.empty()
        self.aliens.empty()
        self.blobs.empty()
        self.update_level_goal()
        self.timer = 0

    def next(self):
        '''start the next level'''
        if self.number < self.max_level:
            self.number += 1
            self.start()

    def restart(self):
        '''restart the game from starting level'''
        sound.level_solved.play()
        self.number = settings.game_starting_level
        self.items.empty()
        self.ship.start_new_game()
        self.start()

    def update(self, dt):
        '''update level status according to passed time dt'''
        self.timer += dt
        self.update_sprites(dt)
        for event in self.events:
            event.update(dt)
        self.update_level_progress()  

    def update_level_goal(self):
        """each level has a different goal,
        update is necessary when changing level"""
        self.goal = self.goals[self.number]
        match self.number:
            case 0:
                self.progress = "Ready?"
                self.alien_random_entrance("big_asteroid",v=settings.alien_speed["big_asteroid"]/2,amount=5,boundary_behaviour="wrap")
                self.alien_random_entrance("small_asteroid",v=settings.alien_speed["small_asteroid"]/2,amount=5,boundary_behaviour="wrap")
                self.alien_random_entrance("blob",v=settings.alien_speed["blob"]/2,energy=9,boundary_behaviour="wrap")
                self.alien_random_entrance("ufo",v=settings.alien_speed["ufo"]/4,boundary_behaviour="wrap")
                self.alien_random_entrance("purple",v=settings.alien_speed["purple"]/2,amount=2,boundary_behaviour="wrap")
            case 1:
                self.alien_random_entrance("big_asteroid",amount=5,boundary_behaviour="reflect")
                self.alien_random_entrance("small_asteroid",amount=5,boundary_behaviour="reflect")
            case 2:
                self.events.append(Event("asteroid_hail", self, random_cycle_time=(800,1200)))
                for n in range(2,10,2):
                    self.aliens.add(Alien(type="purple", level=self, grid=(n,1), direction=(1,1), constraints=pygame.Rect([0,0,Display.screen_width,3*Display.grid_width])))
                for n in range(14,6,-2):
                    self.aliens.add(Alien(type="purple", level=self, grid=(n,5), direction=(-1,-1), constraints=pygame.Rect([0,3*Display.grid_width,Display.screen_width,3*Display.grid_width])))
            case 3:
                self.events.append(Event("asteroid_hail", self, random_cycle_time=(800,1000)))
                self.ufo = Alien(type="ufo", level=self, grid=(1,1), direction=(1,0))
                self.aliens.add(self.ufo)
                for n in [2,6]:
                    self.aliens.add(Alien(type="purple", level=self, grid=(n,1), direction=(1,0), constraints=pygame.Rect([0,0,Display.screen_width,3*Display.grid_width])))
                for n in [10,14]:
                    self.aliens.add(Alien(type="purple", level=self, grid=(n,5), direction=(-1,0), constraints=pygame.Rect([0,3*Display.grid_width,Display.screen_width,3*Display.grid_width]),random_cycle_time=(1200,2000)))
            case 4:
                self.events.append(Event("asteroid_hail", self, random_cycle_time=(1000,1500)))            
                self.alien_random_entrance("blob",boundary_behaviour="reflect")
            case 5:
                self.events.append(Event("asteroid_hail", self, random_cycle_time=(500,800)))
                self.events.append(Event("alien_attack",self,random_cycle_time=(1000,1500)))        

    def update_level_progress(self):
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

    def goal_fulfilled(self):
        '''Return True or False if current goal is fulfilled'''
        match self.number:
            case 1: return not self.asteroids
            case 2: return not self.aliens
            case 3: return self.ufo.energy == 0
            case 4: return not self.blobs
            case 5: return self.timer > 60000

    @property
    def status(self):
        if self.number == 0:
            return "start"
        if self.ship.lives <= 0:         
            return "game_over"
        if self.goal_fulfilled():
            if self.number < self.max_level:
                return "level_solved"
            return "game_won"
        return "running"

    def play_status_sound(self):
        """status sounds are played when a level ends"""
        pygame.mixer.stop()
        match self.status:
            case "game_over":
                sound.game_over.play()
            case "level_solved":
                sound.level_solved.play()
            case "game_won":
                sound.game_won.play()


    def update_sprites(self, dt):
        """update the status of all level objects"""
        for bullet in self.bullets:
            bullet.update(dt)
        self.ship.update(dt)
        for asteroid in self.asteroids:
            asteroid.update(dt)
        for alien in self.aliens:
            alien.update(dt)
        for item in self.items:
            item.update(dt)
        x,y = pygame.mouse.get_pos()
        self.crosshairs.rect.center = x-Display.padding_w, y-Display.padding_h
        self.crosshairs.x = self.crosshairs.rect.x
        self.crosshairs.y = self.crosshairs.rect.y
        self.collision_checks()

    def collision_checks(self):
        """Checks for collisions of sprites, inflicts damage, adds points, generates items"""
        self.bullets_hit()
        self.enemies_hit_ship()
        self.ship_collects_item()
        self.blobs_collide()

    def bullets_hit(self):
        """Check if bullets hit enemies or the ship"""
        # bullets hitting asteroids
        collisions = pygame.sprite.groupcollide(
            self.bullets, self.asteroids, False, False, collided=pygame.sprite.collide_mask)
        for bullet in collisions.keys():
            for asteroid in collisions[bullet]:
                if bullet.type != "missile":
                    asteroid.get_damage(bullet.damage)
                    bullet.kill()
                    asteroid.kill()
                if bullet.type == "missile" and asteroid not in bullet.hit_enemies:
                    # missiles hit each enemy at most once during their explosion time
                    asteroid.get_damage(bullet.damage)
                    asteroid.kill()

        # bullets hitting aliens or the ship
        for bullet in self.bullets:
            if bullet.owner == "player":
                for alien in self.aliens:
                    if pygame.sprite.collide_mask(bullet, alien):
                        if bullet.type != "missile":
                            alien.get_damage(bullet.damage)
                            bullet.kill()
                        if bullet.type == "missile" and alien not in bullet.hit_enemies:
                            # missiles hit each enemy at most once during their explosion time
                            if alien.type == "blob":
                                if alien.energy == 1:
                                    alien.kill()
                                else:
                                    sound.slime_hit.play()
                                    alien.energy = alien.energy//2
                                    alien.change_image(Image.blob[alien.energy-1])
                            else:
                                alien.get_damage(bullet.damage)
                            bullet.hit_enemies.add(alien)
            elif bullet.owner == "enemy" and pygame.sprite.collide_mask(bullet, self.ship):
                if self.ship.status == "shield":
                    bullet.reflect()
                    bullet.owner = "player"
                else:
                    self.ship.get_damage(bullet.damage)
                    bullet.kill()
                    sound.player_hit.play()
            
    def enemies_hit_ship(self):
        """Check if enemies hit the ship"""
        for asteroid in self.asteroids:
            if pygame.sprite.collide_mask(self.ship, asteroid):
                if self.ship.status == "shield" or self.status == "start":
                    asteroid.reflect()
                else:
                    self.ship.get_damage(asteroid.energy)
                    asteroid.energy = 0
                    asteroid.kill()
        for alien in self.aliens:
            if pygame.sprite.collide_mask(self.ship, alien):
                if self.ship.status == "shield" or self.status == "start":
                    alien.reflect()
                else:
                    if self.ship.energy > alien.energy:
                        self.ship.get_damage(alien.energy)
                        alien.energy = 0
                        alien.kill()
                    else:
                        self.ship.get_damage(alien.energy)
        
    def ship_collects_item(self):
        """Check if ship collects an item"""
        for item in self.items:
            if pygame.sprite.collide_mask(self.ship, item):
                if self.ship.status == "shield":
                    item.change_direction(-item.direction[0],-item.direction[1])
                else:
                    self.ship.collect_item(item.type)
                    item.kill()

    def blobs_collide(self):
        """merge colliding blobs if not too big"""
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

    def alien_random_entrance(self, type, amount=1, energy=None, v=None, constraints = None, boundary_behaviour = "vanish"):
            constraints = constraints or pygame.Rect(0, 0, Display.screen_width, Display.screen_height)
            v = v or settings.alien_speed[type]
            for i in range(amount):
                alien = Alien(type, self, energy=energy, v=v, constraints=constraints, boundary_behaviour = boundary_behaviour)
                alien.change_direction(random()*(constraints.w-alien.w)+constraints.x-alien.x, constraints.bottom-alien.rect.bottom)
                alien.change_position(x=random()*(constraints.w-alien.w)+constraints.x, y=constraints.y-alien.h)           
                if type in ["big_asteroid","small_asteroid"]:
                    self.asteroids.add(alien)
                elif type == "blob":
                    if self.status != "start":
                        sound.blob_spawns.play()
                    self.blobs.add(alien)
                    self.aliens.add(alien)
                else:
                    self.aliens.add(alien)
            if type == "blob" and self.status != "start":
                    sound.blob_spawns.play()