import pygame
import settings

screen = pygame.display.set_mode(
            (settings.screen_width, settings.screen_height))


class Image:
    def __init__(self, path, colorkey=(0,0,0), scaling_width=None):
        raw_image = pygame.image.load(path)#.convert_alpha()
        raw_image.set_colorkey(colorkey)
        #raw_image.set_alpha(1)
        bounding_rect = raw_image.get_bounding_rect(min_alpha=1)
        self.surface = pygame.Surface(bounding_rect.size)
        self.surface.blit(raw_image,(0,0),bounding_rect)
        self.rect = self.surface.get_rect()
        self.w = self.rect.w
        self.h = self.rect.h
        self.surface.set_colorkey(colorkey)
        if scaling_width:
            self.rescale(width=scaling_width)

    def rescale(self, width=100):
        factor = width / self.w
        self.surface = pygame.transform.scale(
            self.surface, (factor*self.w, factor*self.h))
        self.rect = self.surface.get_rect()
        self.w = self.rect.w
        self.h = self.rect.h

    def blit(self, screen):
        screen.blit(self.surface, self.rect, colorkey=self.surface.get_colorkey())

    cache = {}
    @classmethod
    def load(cls, path, colorkey=(0,0,0), scaling_width=None):
        if path not in cls.cache:
            cls.cache[path] = Image(path, colorkey, scaling_width)
        return cls.cache[path]

"""ship = {1: Image('images/ship/a-03.png'),
        2: Image('images/ship/a-02.png'), 3: Image('images/ship/a-01.png')}
bullet = {1: Image('images/bullet/1.png'),
          2: Image('images/bullet/2.png'), 3: Image('images/bullet/3.png')}
alien = {"big_asteroid": Image('images/asteroid/1.png'), "small_asteroid": Image('images/asteroid/2.png'),
         "purple": Image('images/alien/1.png',colorkey=(255,255,255)), "ufo": Image('images/alien/2.png'), 3: Image('images/alien/1.png')}
alien["big_asteroid"].rescale(100)
alien["small_asteroid"].rescale(50)
alien["purple"].rescale()
alien["ufo"].rescale()
ship[1].rescale(100)
ship[2].rescale(100)
ship[3].rescale(120)
"""