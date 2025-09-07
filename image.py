import pygame
import settings
#import pickle

screen = pygame.display.set_mode(
            (settings.screen_width, settings.screen_height))


class Image:
    '''Class to manage loading images to be used as surfaces for sprites.
    (Inheriting properties from the 'Surface'-class is not be possible in pygame)'''
    def __init__(self, surface, mask, colorkey = None, reflected = False):
        self.surface = surface
        self.mask = mask
        if colorkey:
            self.surface.set_colorkey(colorkey)

    @property
    def rect(self):
        return self.surface.get_rect()
    
    @property
    def w(self):
        return self.rect.w
    
    @property
    def h(self):
        return self.rect.h

    def scale_by(self, factor):
        return Image(pygame.transform.scale(self.surface, (factor*self.w, factor*self.h)),
            self.mask.scale((factor*self.w, factor*self.h)))

    def rescale(self, width):
        factor = width / self.w
        scale_by(self, factor)

    cache = {}
    @classmethod
    def load(cls, path, colorkey=(0,0,0), scaling_width=None, scaling_height=None, scaling_factor=None):
        '''lazy image loader, each image gets loaded and formated only once,
            either the desired width or height can be specified
            path: either a single path as a string oder a list of paths as strings'''
        if isinstance(path, str):
            if path in cls.cache:
                return cls.cache[path]
            else:
                #loads images, trims their boundary and makes it transparent
                raw_image = pygame.image.load(path)
                if colorkey != (0,0,0):
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
                    surface = pygame.Surface(bounding_rect.size)
                    surface.blit(masked_image,(0,0),bounding_rect)
                    surface.set_colorkey((0,0,0))
                else:
                    bounding_rect = raw_image.get_bounding_rect()
                    surface = pygame.Surface(bounding_rect.size)
                    surface.blit(raw_image,(0,0),bounding_rect)
                    surface.set_colorkey((0,0,0))
                if scaling_width:
                    factor = scaling_width / bounding_rect.w
                    surface = pygame.transform.scale(
                                surface, (factor*bounding_rect.w, factor*bounding_rect.h))
                elif scaling_height:
                    factor = scaling_height / bounding_rect.h
                    surface = pygame.transform.scale(
                                surface, (factor*bounding_rect.w, factor*bounding_rect.h))
                elif scaling_factor:
                    surface = pygame.transform.scale(
                                surface, (scaling_factor*bounding_rect.w, scaling_factor*bounding_rect.h))


                mask = pygame.mask.from_surface(surface)
                image = Image(surface, mask)
                cls.cache[path] = image
                return image
        else:
            return [load(cls, frame_path, colorkey, scaling_width, scaling_height, scaling_factor) for frame_path in path]

    reflected_cache ={}
    @classmethod
    def reflect(cls, image, flip_x, flip_y):
        if id(image.surface) in cls.reflected_cache:
            return cls.reflected_cache[id(image.surface)]
        else:
            flipped_surface = pygame.transform.flip(image.surface, flip_x=flip_x, flip_y=flip_y)
            flipped_image = Image(flipped_surface, pygame.mask.from_surface(flipped_surface))
            cls.reflected_cache[id(image.surface)] = flipped_image
            return flipped_image

    def blit(self, screen):
        screen.blit(self.surface, self.rect, colorkey=self.surface.get_colorkey())