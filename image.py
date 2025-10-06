import pygame, settings
from pathlib import Path
from display import Display
from settings import Color

class Image:
    '''Class to manage loading images to be used as surfaces for sprites.
    (Inheriting properties directly from the 'Surface'-class is not be possible in pygame)'''
    def __init__(self, surface, mask, colorkey = None, reflected = False, path = None):
        self.surface = surface
        self.mask = mask
        self.path = path
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
        '''Rescale image and its mask by a given factor'''
        return Image(pygame.transform.scale(self.surface, (factor*self.w, factor*self.h)).convert_alpha(),
            self.mask.scale((factor*self.w, factor*self.h)))

    def rescale(self, scaling_width=None, scaling_height=None, scaling_factor=None):
        '''Allows rescaling images either to a given width, height or by a factor'''
        factor = None
        if scaling_width:
            factor = Display.grid_width/settings.GRID_WIDTH * scaling_width / self.w
        elif scaling_height:
            factor = Display.grid_width/settings.GRID_WIDTH * scaling_height / self.h
        elif scaling_factor:
            factor = scaling_factor
        if factor is None:
            return self
        return self.scale_by(factor)

    @classmethod
    def determine_scaling_width(cls, path):
        '''Depending on the prefix of the path and the properties in settings.py,
        return the optimal scaling width for the image with given path'''
        path_obj = Path(path)
        parts = path_obj.parts
        if parts[0] == "images":
            match parts[1]:
                case "item":
                    return settings.Item.SIZE
                case "alien":
                    return settings.alien_width[Path(parts[2]).stem]
                case "bullet":
                    return settings.bullet_width[Path(parts[2]).stem]
                case "ship":
                    ship_rank = int(parts[2][2])
                    return settings.Ship.WIDTH[ship_rank]
                case "statusbar":
                    return 72 #height of the empty health bar picture
                case _:
                    raise ValueError(f"No scaling rule for path {path}")
        raise ValueError(f"image path should start with 'images'")

    cache = {}
    @classmethod
    def load(cls, path, colorkey=Color.BLACK, scaling_width=None, scaling_height=None, scaling_factor=None):
        '''lazy image loader, each image gets loaded and formated only once,
            either the desired width or height can be specified
            path: either a single path as a string oder a list of paths as strings'''
        if isinstance(path, str):
            if path in cls.cache:
                return cls.cache[path].rescale(scaling_width=scaling_width, scaling_height=scaling_height, scaling_factor=scaling_factor)
            path_obj = Path(path)
            if path_obj.is_dir():
                # load all images in the given directory
                image_paths = sorted([str(image_path) for image_path in path_obj.iterdir() if image_path.is_file()])
                return [cls.load(image_path, colorkey, scaling_width, scaling_height, scaling_factor) for image_path in image_paths]
            relpath = Path(path_obj).relative_to("images")
            newpath = Path(f"preprocessed_images/grid_width={Display.grid_width}" / relpath)

            if newpath.exists():
                #if the image has been preprocessed before, load it into the games cache
                surface = pygame.image.load(newpath)
                mask = pygame.mask.from_surface(surface)
                image = Image(surface, mask, path = path)
                cls.cache[path] = image
                return image.rescale(scaling_width=scaling_width, scaling_height=scaling_height, scaling_factor=scaling_factor)

            #loads image
            raw_image = pygame.image.load(path)
            #If boundary is not black, we first need to remove it without
            #losing pixels in the inside of the figure
            if colorkey != Color.BLACK: 
                temp = raw_image.copy()
                temp.set_colorkey(colorkey)
                #temp has now transparent boundary, but unfortunately
                #maybe also transparent pixels in the inside
                temp_mask = pygame.mask.from_surface(temp)
                temp_mask.invert() #the inverted mask covers all transparent pixels
                temp_mask = temp_mask.connected_component() #this component is exactly the boundary
                temp_mask.invert() #its inverse is the mask of the actual figure on the image
                alpha_surf = temp_mask.to_surface(setcolor=(255,255,255,255),
                                                      unsetcolor=(0,0,0,0))
                new_raw = pygame.Surface(raw_image.get_size(), pygame.SRCALPHA)
                new_raw.blit(raw_image, (0,0))
                new_raw.blit(alpha_surf, (0,0), special_flags=pygame.BLEND_RGBA_MULT)
                raw_image = new_raw # now its boundary is transparent
            bounding_rect = raw_image.get_bounding_rect()
            surface = pygame.Surface(bounding_rect.size, pygame.SRCALPHA)
            #surface now has its boundary trimmed to the smallest rectangle
            #containing the complete figure
            surface.blit(raw_image,(0,0),bounding_rect)
            mask = pygame.mask.from_surface(surface)
                
            #rescales the image according to user's screen settings and caches the result
            image = Image(surface, mask, path = path).rescale(scaling_width = Image.determine_scaling_width(path))
            #preprocessed surfaces get stored for the next game
            newpath.parent.mkdir(parents=True, exist_ok=True)
            pygame.image.save(image.surface, str(newpath))
            #and cached for further uses in the current game
            cls.cache[path] = image

            return image.rescale(scaling_width=scaling_width, scaling_height=scaling_height, scaling_factor=scaling_factor)
        return [cls.load(frame_path, colorkey, scaling_width, scaling_height, scaling_factor) for frame_path in path]

    reflected_cache = {}
    @classmethod
    def reflect(cls, image, flip_x, flip_y):
        if not (flip_x or flip_y):
            return image
        if (image.path, image.w, image.h, flip_x, flip_y) in cls.reflected_cache.keys():
            return cls.reflected_cache[(image.path, image.w, image.h, flip_x, flip_y)]
        flipped_surface = pygame.transform.flip(image.surface, flip_x=flip_x, flip_y=flip_y)
        flipped_image = Image(flipped_surface, pygame.mask.from_surface(flipped_surface), path = image.path)
        cls.reflected_cache[(image.path, image.w, image.h, flip_x, flip_y)] = flipped_image
        return flipped_image            

    def blit(self, screen):
        screen.blit(self.surface, self.rect, colorkey=self.surface.get_colorkey())

    # blob and blubber images
    @classmethod
    def load_blob(cls):
        N=settings.BLOB.energy
        raw_blob = cls.load("images/alien/blob", colorkey=settings.BLOB.colorkey)
        cls.blob = [raw_blob[2].scale_by((N/n)**(-1/3)) for n in range(1,N//8)]+[raw_blob[1].scale_by((N/n)**(-1/3)) for n in range(N//8,N//4+1)]+[raw_blob[0].scale_by((N/n)**(-1/3)) for n in range(N//4+1, N+1)]
        raw_blubber = cls.load(f'images/bullet/blubber.png')
        cls.blubber = [raw_blubber.scale_by((N/n)**(-1/3)) for n in range(1,N+1)]
        cls.reflected_blubber = [cls.reflect(image, flip_x=True, flip_y=True) for image in cls.blubber]