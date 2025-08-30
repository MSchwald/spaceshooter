import pygame
from pygame.locals import *
from alien import Alien

lst = {1: [(100, 100, "big_asteroid", [1, 2]), (200, 100, "small_asteroid", [1, 0])], 2: [
    (100, 100, 1, [1, 1]), (300, 100, 1, [1, 1]), (500, 100, 1, [1, 1])], 3: [(100, 100, 2, [2, 0])]}
max_level = max(lst.keys())


class Level:
    """A class to manage the game levels"""

    def __init__(self, number):
        self.number = number
        self.aliens = pygame.sprite.Group()

    def start(self, ship):
        ship.reset_position()
        # Resets the Group of aliens
        self.aliens.empty()
        for (x, y, type, direction) in lst[self.number]:
            self.aliens.add(Alien(x, y, type, direction=direction))

    def next(self, ship):
        if self.number < max_level:
            self.number += 1
            ship.set_level(min(3, ship.level+1))
            self.start(ship)

    def restart(self, ship):
        self.number = 1
        ship.start_new_game()
        self.start(ship)
