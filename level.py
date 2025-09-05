import pygame, settings
from pygame.locals import *
from ship import Ship
from alien import Alien
import sound

#placement of enemies in an 16x9-grid
lst = {1: [(4, 1, "big_asteroid", "random"), (6, 1, "big_asteroid", (0,1)), (9, 1, "big_asteroid", (0,1)), (11, 1, "big_asteroid", "random"), (2, 1, "small_asteroid", "random"), (13, 1, "small_asteroid", "random")],
2: [(1, 1, "purple", (1, 1)), (3, 1, "purple", (1, 1)), (5, 1, "purple", (1, 1))],
3: [(1, 1, "ufo", (2, 0))]}
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
        self.aliens = pygame.sprite.Group()
        self.items = pygame.sprite.Group()


    def status(self):
        if self.ship.lives <= 0:
            sound.game_over.play()
            return "game over"
        elif not self.aliens:
            if self.number < max_level:
                sound.start.play()
                return "solved"
            else:
                pygame.mixer.stop()
                sound.game_won.play()
                return "game won"
        else:
            return "running"

    def start(self):
        self.ship.reset_position()
        # Resets the Groups of bullets and aliens
        self.ship_bullets.empty()
        self.bullets.empty()
        self.aliens.empty()
        for (x, y, type, direction) in lst[self.number]:
            self.aliens.add(Alien(type=type, level=self, grid=(x,y), direction=direction))

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

    
