import pygame, sound
from ship import Ship
from alien import Alien
from random import random, randint
from math import hypot
from event import Event
from sprite import Sprite
from image import Image, GraphicData
from statusbar import Statusbar
from display import Display
from settings import AlienTemplate, ALIEN, SHIP, BULLET
from physics import Vector, normalize

class Level:
    """Manage loading and logic of game levels and their ingame objects"""

    def __init__(self, number):
        """Initialize ingame objects and sprite groups"""
        self.ship = Ship(self)
        self.statusbar = Statusbar(self)
        self.crosshairs = Sprite(GraphicData(path = 'images/bullet/aim.png', scaling_width = BULLET.MISSILE.width))
        Image.load_blob()
        self.number = number
        self.goals = ["Welcome!","Destroy all asteroids!","Defeat all aliens!","Defeat the ufo!","Defeat the blob!","Survive for a minute!"]
        self.max_level = len(self.goals) - 1
        self.boundary_behaviour = None

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
        for group in [self.bullets, self.asteroids, self.aliens, self.items]:
            for sprite in group:
                sprite.blit(screen)
        self.ship.blit(screen)
        self.crosshairs.blit(screen)

    def start_current(self):
        """(re)start current level"""
        self.ship.reset_pos()
        self.timer = 0
        self.goal = self.goals[self.number]
        self.events=[]
        for group in [self.ship_bullets, self.bullets,
                    self.asteroids, self.aliens, self.blobs]:
            group.empty()
        self.load_level(self.number)

    def start_next(self):
        """start the next level"""
        if self.number < self.max_level:
            self.number += 1
            self.start_current()

    def restart_game(self):
        '''restart from starting level'''
        sound.level_solved.play()
        self.number = SHIP.GAME_LEVEL
        self.items.empty()
        self.ship.start_new_game()
        self.start_current()

    def load_level(self, number):
        """load enemies and level events"""
        match number:
            case 0:
                self.boundary_behaviour = "wrap"
                self.alien_random_entrance(ALIEN.BIG_ASTEROID,speed=ALIEN.BIG_ASTEROID.speed/2,amount=5)
                self.alien_random_entrance(ALIEN.SMALL_ASTEROID,speed=ALIEN.SMALL_ASTEROID.speed/2,amount=5)
                self.alien_random_entrance(ALIEN.BLOB,speed=ALIEN.BLOB.speed/2,energy=9)
                self.alien_random_entrance(ALIEN.UFO,speed=ALIEN.UFO.speed/4)
                self.alien_random_entrance(ALIEN.PURPLE,speed=ALIEN.PURPLE.speed/2,amount=2)
            case 1:
                self.boundary_behaviour = "reflect"
                self.alien_random_entrance(ALIEN.BIG_ASTEROID,amount=5)
                self.alien_random_entrance(ALIEN.SMALL_ASTEROID,amount=5)
            case 2:
                self.boundary_behaviour = "reflect"
                self.events.append(Event("asteroid_hail", self, random_cycle_time=(800,1200)))
                for n in range(2,10,2):
                    alien_n = Alien(ALIEN.PURPLE, level=self, direction=Vector(1,1), constraints=pygame.Rect([0,0,Display.screen_width,3*Display.grid_width]))
                    alien_n.spawn(grid=(n,1))
                    self.aliens.add(alien_n)
                for n in range(14,6,-2):
                    alien_n = Alien(ALIEN.PURPLE, level=self, direction=Vector(-1,-1), constraints=pygame.Rect([0,3*Display.grid_width,Display.screen_width,3*Display.grid_width]))
                    alien_n.spawn(grid=(n,5))
                    self.aliens.add(alien_n)
            case 3:
                self.boundary_behaviour = "reflect"
                self.events.append(Event("asteroid_hail", self, random_cycle_time=(800,1000)))
                self.ufo = Alien(ALIEN.UFO, level=self, direction=Vector(1,0))
                self.ufo.spawn(grid=(1,1))
                self.aliens.add(self.ufo)
                for n in [2,6]:
                    alien_n = Alien(ALIEN.PURPLE, level=self, direction=Vector(1,0), constraints=pygame.Rect([0,0,Display.screen_width,3*Display.grid_width]))
                    alien_n.spawn(grid=(n,1))
                    self.aliens.add(alien_n)
                for n in [10,14]:
                    alien_n = Alien(ALIEN.PURPLE, level=self, direction=Vector(-1,0), constraints=pygame.Rect([0,3*Display.grid_width,Display.screen_width,3*Display.grid_width]))
                    alien_n.spawn(grid=(n,5))
                    self.aliens.add(alien_n)
            case 4:
                self.boundary_behaviour = "reflect"
                self.events.append(Event("asteroid_hail", self, random_cycle_time=(1000,1500)))            
                self.alien_random_entrance(ALIEN.BLOB)
            case 5:
                self.boundary_behaviour = "reflect"
                self.events.append(Event("asteroid_hail", self, random_cycle_time=(500,800)))
                self.events.append(Event("alien_attack", self, random_cycle_time=(1000,1500)))        

    @property
    def progress(self):
        match self.number:
            case 0: return "Ready?"
            case 1: return f"{len(self.asteroids)} left"
            case 2: return f"{len(self.aliens)} left"
            case 3: return f"Ufo health: {self.ufo.energy}"
            case 4: return f"Blob energy: {sum([blob.energy for blob in self.blobs])}"
            case 5: return f"Timer: {int(60-self.timer/1000)}"
            case _: return ""

    @property
    def goal_fulfilled(self):
        '''Return True or False if current goal is fulfilled'''
        match self.number:
            case 1: return not self.asteroids
            case 2: return not self.aliens
            case 3: return self.ufo.energy == 0
            case 4: return not self.blobs
            case 5: return self.timer > 60000
            case _: return False

    @property
    def status(self):
        if self.number == 0:
            return "start"
        if self.ship.lives <= 0:         
            return "game_over"
        if self.goal_fulfilled:
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

    def update(self, dt):
        '''update level status according to passed time dt'''
        self.timer += dt
        self.update_sprites(dt)
        for event in self.events:
            event.update(dt)

    def update_sprites(self, dt):
        """update the status of all level objects"""
        for group in [self.bullets, self.asteroids, self.aliens, self.items]:
            for sprite in group:
                sprite.update(dt)
        self.ship.update(dt)
        self.update_crosshairs()
        self.collision_checks()

    def update_crosshairs(self):
        x,y = pygame.mouse.get_pos()
        self.crosshairs.spawn(center=Vector(x - Display.padding_w, y - Display.padding_h))

    def collision_checks(self):
        """Check for collisions of sprites, inflict damage, add points, generate items"""
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
                if bullet.template.name != "explosion":
                    asteroid.get_damage(bullet.damage)
                    bullet.kill()
                    asteroid.kill()
                if bullet.template.name == "explosion" and asteroid not in bullet.hit_enemies:
                    # missiles hit each enemy at most once during their explosion time
                    asteroid.get_damage(bullet.damage)
                    asteroid.kill()

        # bullets hitting aliens or the ship
        for bullet in self.bullets:
            if bullet.owner == "player":
                for alien in self.aliens:
                    if pygame.sprite.collide_mask(bullet, alien):
                        if bullet.template.name != "explosion":
                            alien.get_damage(bullet.damage)
                            bullet.kill()
                        if bullet.template.name == "explosion" and alien not in bullet.hit_enemies:
                            # missiles hit each enemy at most once during their explosion time
                            if alien.template.name == "blob":
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
                    item.vel *= -1
                else:
                    self.ship.collect_item(item)
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
                        and blob1.energy + blob2.energy <= ALIEN.BLOB.energy
                        and pygame.sprite.collide_mask(blob1, blob2)
                    ):
                        dpdv = (blob1.center - blob2.center) * (blob1.vel - blob2.vel)
                        if dpdv < 0:
                            merge_occured = True            
                            merged_blob = Alien.merge(blob1, blob2)
                            self.aliens.add(merged_blob)
                            self.blobs.add(merged_blob)
                            blob1.hard_kill()
                            blob2.hard_kill()
                            sound.blob_merge.play()
                            break

    def alien_random_entrance(self, template: AlienTemplate,
                            amount: int = 1,
                            energy: int | None = None,
                            speed: float | None = None,
                            constraints: pygame.Rect | None = None,
                            boundary_behaviour: str | None = None):
            speed = speed or template.speed
            constraints = constraints or Display.screen_rect
            boundary_behaviour = boundary_behaviour or self.boundary_behaviour
            for i in range(amount):
                alien_i = Alien(template, level=self, energy=energy, speed = speed,
                            constraints=constraints, boundary_behaviour = boundary_behaviour)
                # alien spawns at random point over the screen
                spawning_pos = Vector(
                    constraints.x + random() * (constraints.w - alien_i.w),
                    constraints.y - alien_i.h
                )

                # alien aims for a random point on the bottom of the screen
                target = Vector(
                    constraints.x + random() * (constraints.w - alien_i.w),
                    constraints.bottom
                )
                alien_i.vel = speed * normalize(target - spawning_pos)
                alien_i.spawn(pos = spawning_pos)           
                if template.name in ["big_asteroid","small_asteroid"]:
                    self.asteroids.add(alien_i)
                elif template.name == "blob":
                    self.blobs.add(alien_i)
                    self.aliens.add(alien_i)
                else:
                    self.aliens.add(alien_i)