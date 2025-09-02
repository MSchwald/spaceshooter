import pygame
import settings

screen = pygame.display.set_mode(
            (settings.screen_width, settings.screen_height))


class Image:
    '''Class to manage loading images to be used as surfaces for sprites.
    (Inheriting properties from the 'Surface'-class is not be possible in pygame)'''
    def __init__(self, path, colorkey=(0,0,0), scaling_width=None):
        #loads images, trims their boundary and makes it transparent
        raw_image = pygame.image.load(path)
        # colorkey:
        temp = raw_image.copy()
        temp.set_colorkey(colorkey)
        mask = pygame.mask.from_surface(temp)
        mask.invert()
        mask = mask.connected_component()
        mask.invert()
        masked_image = mask.to_surface(surface=raw_image, setcolor=None)
        temp = masked_image.copy()
        temp.set_colorkey((0,0,0))
        bounding_rect = masked_image.get_bounding_rect()
        self.surface = pygame.Surface(bounding_rect.size)
        self.surface.blit(masked_image,(0,0),bounding_rect)
        self.surface.set_colorkey((0,0,0))
        self.rect = self.surface.get_rect()
        self.w = self.rect.w
        self.h = self.rect.h
        if scaling_width:
            self.rescale(width=scaling_width)
        self.mask = pygame.mask.from_surface(self.surface)

    def rescale(self, width=100):
        factor = width / self.w
        self.surface = pygame.transform.scale(
            self.surface, (factor*self.w, factor*self.h))
        self.rect = self.surface.get_rect()
        self.w = self.rect.w
        self.h = self.rect.h
        print(self.rect)

    def blit(self, screen):
        screen.blit(self.surface, self.rect, colorkey=self.surface.get_colorkey())

    cache = {}
    @classmethod
    def load(cls, path, colorkey=settings.bg_color, scaling_width=None):
        #lazy image loader, each image gets loaded only once
        if path not in cls.cache:
            cls.cache[path] = Image(path, colorkey, scaling_width)
        return cls.cache[path]