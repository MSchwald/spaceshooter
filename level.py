import pygame, settings
from pygame.locals import *
from alien import Alien

#placement of enemies in an 16x9-grid
lst = {1: [(4, 1, "big_asteroid", "random"), (6, 1, "big_asteroid", (0,1)), (9, 1, "big_asteroid", (0,1)), (11, 1, "big_asteroid", "random"), (2, 1, "small_asteroid", "random"), (13, 1, "small_asteroid", "random")],
2: [(1, 1, "purple", (1, 1)), (3, 1, "big_asteroid", (1, 1)), (5, 1, "purple", (1, 1))],
3: [(1, 1, "ufo", (2, 0))]}
max_level = max(lst.keys())


class Level:
    """A class to manage the game levels"""

    def __init__(self, number):
        self.number = number
        self.bullets = pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()
        self.items = pygame.sprite.Group()

    def status(self, ship):
        if ship.lives <= 0:
            return "game over"
        elif not self.aliens:
            if self.number < max_level:
                return "solved"
            else:
                return "game won"
        else:
            return "running"

    def start(self, ship):
        ship.reset_position()
        # Resets the Groups of bullets and aliens
        self.bullets.empty()
        self.aliens.empty()
        for (x, y, type, direction) in lst[self.number]:
            self.aliens.add(Alien(grid=[x,y], type=type, direction=direction))

    def next(self, ship):
        if self.number < max_level:
            self.number += 1
            self.start(ship)

    def restart(self, ship):
        self.number = 1
        self.items.empty()
        ship.start_new_game()
        self.start(ship)
