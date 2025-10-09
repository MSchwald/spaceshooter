import pygame, sound
from ship import Ship
from alien import Alien
from random import random, randint
from math import hypot
from sprite import Sprite
from image import Image, GraphicData
from display import Display
from timer import ActionTimer, Timer
from settings import AlienTemplate, ALIEN, SHIP, BULLET
from physics import Vector, normalize
from dataclasses import dataclass

class Level:
    """Manage loading and logic of game levels and their ingame objects"""

    def __init__(self, number):
        """Initialize ingame objects and sprite groups"""
        self.ship = Ship(self)
        self.crosshairs = Sprite(GraphicData(path = 'images/bullet/aim.png', scaling_width = BULLET.MISSILE.width))
        Image.load_blob()
        self.number = number
        self.goals = ["Welcome!","Destroy all asteroids!","Defeat all aliens!","Defeat the ufo!","Defeat the blob!","Survive for a minute!"]
        self.max_level = len(self.goals) - 1
        self.boundary_behaviour = None

        # empty sprite groups
        self.ship_bullets = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.items = pygame.sprite.Group()
        self.asteroids = pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()
        self.ufos = pygame.sprite.Group()
        self.blobs = pygame.sprite.Group()

        self.timer = Timer()
        self.asteroid_hail = ActionTimer()
        self.alien_hail = ActionTimer()

        self.timers = (self.timer, self.asteroid_hail, self.alien_hail)
        
    def blit(self, screen = None):
        """blit the current state of the level"""
        screen = screen or Display.screen
        for group in [self.bullets, self.asteroids, self.aliens, self.items]:
            for sprite in group:
                sprite.blit(screen)
        self.ship.blit(screen)
        self.crosshairs.blit(screen)

    def start_current(self):
        """(re)start current level"""
        self.ship.reset_pos()
        for timer in self.timers:
            timer.reset()
        self.goal = self.goals[self.number]

        for group in [self.ship_bullets, self.bullets, self.ufos,
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

    def alien_spawn(self, alien: Alien, **kwargs):
        alien.spawn(**kwargs)
        match alien.template.name:
            case "big_asteroid" | "small_asteroid":
                self.asteroids.add(alien)
            case "blob":
                self.blobs.add(alien)
                self.aliens.add(alien)
            case "ufo":
                self.ufos.add(alien)
                self.aliens.add(alien)
            case "purple":
                self.aliens.add(alien)

    def alien_random_entrance(self, alien: Alien):
            '''alien spawns at random point over the screen
            and aims for a random point on the bottom'''
            constraints = alien.constraints
            spawning_pos = Vector(
                constraints.x + random() * (constraints.w - alien.w),
                constraints.y - alien.h
            )
            target_pos = Vector(
                constraints.x + random() * (constraints.w - alien.w),
                constraints.bottom
            )
            alien.vel = alien.speed * normalize(target_pos - spawning_pos)
            self.alien_spawn(alien, pos = spawning_pos)   

    def encounter(self, template: AlienTemplate,
                    amount: int = 1,
                    grid: tuple[int, int] | None = None,
                    speed_factor: float = 1,
                    dir: tuple[int, int] | None = None,
                    energy: int | None = None,
                    constraints: pygame.Rect | None = Display.screen,
                    boundary_behaviour: str | None = None):
        if dir is not None:
            direction = Vector(dir[0], dir[1])
        else:
            direction = None
        boundary_behaviour = boundary_behaviour or self.boundary_behaviour
        for _ in range(amount):
            alien = Alien(template = template, level = self, energy = energy,
                    speed = template.speed * speed_factor, direction = direction,
                    constraints = constraints, boundary_behaviour = boundary_behaviour)
            if grid is not None:
                self.alien_spawn(alien, grid = grid)
            else:
                self.alien_random_entrance(alien)

    def load_level(self, number):
        """load enemies and start action timers"""
        match number:
            case 0:
                self.boundary_behaviour = "wrap"
                self.encounter(ALIEN.BIG_ASTEROID, 5, speed_factor = 1/2)
                self.encounter(ALIEN.SMALL_ASTEROID, 5, speed_factor = 1/2)
                self.encounter(ALIEN.BLOB, speed_factor = 1/2, energy = 9)
                self.encounter(ALIEN.UFO, speed_factor = 1/4)
                self.encounter(ALIEN.PURPLE, 2, speed_factor = 1/2)
            case 1:
                self.boundary_behaviour = "reflect"
                self.encounter(ALIEN.BIG_ASTEROID, 5)
                self.encounter(ALIEN.SMALL_ASTEROID, 5)
            case 2:
                self.asteroid_hail.reset(cycle_min = 800, cycle_max = 1000)
                self.boundary_behaviour = "reflect"
                for n in (2,4,6,8):
                    self.encounter(ALIEN.PURPLE, grid = (n,1), dir = (1,1), constraints = Display.grid_rect(0, 0, 16, 3))
                for n in (8,10,12,14):
                    self.encounter(ALIEN.PURPLE, grid = (n,5), dir = (-1,-1), constraints = Display.grid_rect(0, 3, 16, 3))
            case 3:
                self.asteroid_hail.reset(cycle_min = 800, cycle_max = 1000)
                self.boundary_behaviour = "reflect"
                self.encounter(ALIEN.UFO, grid = (1,1), dir = (1,0))
                self.encounter(ALIEN.PURPLE, grid = (2,3), dir = (1,0))
                self.encounter(ALIEN.PURPLE, grid = (6,3), dir = (1,0))
                self.encounter(ALIEN.PURPLE, grid = (10,5), dir = (-1,0))
                self.encounter(ALIEN.PURPLE, grid = (14,5), dir = (-1,0))
            case 4:
                self.asteroid_hail.reset(cycle_min = 800, cycle_max = 1000)
                self.boundary_behaviour = "reflect"           
                self.encounter(ALIEN.BLOB)
            case 5:
                self.asteroid_hail.reset(cycle_min = 500, cycle_max = 800)
                self.alien_hail.reset(cycle_min = 1000, cycle_max = 1500)

    @property
    def progress(self):
        match self.number:
            case 0: return "Ready?"
            case 1: return f"{len(self.asteroids)} left"
            case 2: return f"{len(self.aliens)} left"
            case 3:
                if not self.ufos:
                    return f"Ufo health: 0"
                ufo = next(iter(self.ufos))
                return f"Ufo health: {ufo.energy}"
            case 4: return f"Blob energy: {sum([blob.energy for blob in self.blobs])}"
            case 5: return f"Timer: {int(60-self.timer.total_time/1000)}"
            case _: return ""

    @property
    def goal_fulfilled(self):
        '''Return True or False if current goal is fulfilled'''
        match self.number:
            case 1: return not self.asteroids
            case 2: return not self.aliens
            case 3: return not self.ufos
            case 4: return not self.blobs
            case 5: return self.timer.total_time > 60000
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
        for timer in self.timers:
            timer.update(dt)
        if self.asteroid_hail.check_alarm():
            self.encounter(ALIEN.BIG_ASTEROID, boundary_behaviour = "vanish")
        if self.alien_hail.check_alarm():
            if random() > 0.5:
                self.encounter(ALIEN.PURPLE, boundary_behaviour = "reflect")
            else:
                self.encounter(ALIEN.BLOB, energy = ALIEN.BLOB.energy//4)
        self.update_sprites(dt)

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
