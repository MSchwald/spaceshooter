import pygame
import settings


class Image:
    def __init__(self, path):
        self.surface = pygame.image.load(path)
        self.rect = self.surface.get_rect()
        self.w = self.rect.w
        self.h = self.rect.h

    def rescale(self, max_width=100):
        factor = max_width / self.w
        self.surface = pygame.transform.scale(
            self.surface, (factor*self.w, factor*self.h))
        self.rect = self.surface.get_rect()
        self.w = self.rect.w
        self.h = self.rect.h

    def blit(self, screen):
        screen.blit(self.surface, self.rect)


ship = {1: Image('images/ship/1.png'),
        2: Image('images/ship/2.png'), 3: Image('images/ship/3.png')}
bullet = {1: Image('images/bullet/1.png'),
          2: Image('images/bullet/2.png'), 3: Image('images/bullet/3.png')}
alien = {"big_asteroid": Image('images/asteroid/1.png'), "small_asteroid": Image('images/asteroid/2.png'),
         1: Image('images/alien/1.png'), 2: Image('images/alien/2.png'), 3: Image('images/alien/1.png')}
alien["big_asteroid"].rescale(100)
alien["small_asteroid"].rescale(50)
alien[1].rescale()
alien[2].rescale()
ship[3].rescale(120)
print([(image.w, image.h) for image in ship.values()])
