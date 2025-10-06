import pygame
from pathlib import Path
from display import Display
from settings import COLOR, SCREEN, ITEM, ALIEN, SHIP, BULLET
from dataclasses import dataclass

class Image:
    '''Manage lazy loading and transforming images and masks to be used for sprites'''
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
            factor = Display.grid_width/SCREEN.GRID_WIDTH * scaling_width / self.w
        elif scaling_height:
            factor = Display.grid_width/SCREEN.GRID_WIDTH * scaling_height / self.h
        elif scaling_factor:
            factor = scaling_factor
        if factor is None:
            return self
        return self.scale_by(factor)

    @classmethod 
    def determine_scaling_width(cls, path): # obsolete now?
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
                    return SHIP.WIDTH[ship_rank]
                case "statusbar":
                    return 72 #height of the empty health bar picture
                case _:
                    raise ValueError(f"No scaling rule for path {path}")
        raise ValueError(f"image path should start with 'images'")

    cache = {}
    @classmethod
    def load(cls, path, colorkey=COLOR.BLACK, scaling_width=None, scaling_height=None, scaling_factor=None):
        '''Loads image with given path (as a string with or without the png-suffix) lazily.
            Background of color 'colorkey' gets cropped and transparent.
            Rescales result either to desired width, height (in standard resolution)
            or by a given scaling factor.
            Result gets cached and saved for quicker access.'''
        if path in cls.cache:
            return cls.cache[path].rescale(scaling_width=scaling_width, scaling_height=scaling_height, scaling_factor=scaling_factor)
        path_obj = Path(path)
        if not path_obj.suffix:
            path_obj = path_obj.with_suffix(".png")
        relpath = Path(path_obj).relative_to("images")
        newpath = Path(f"preprocessed_images/grid_width={Display.grid_width}" / relpath)

        if newpath.exists():
            # if the image has been preprocessed before, load it into the games cache
            surface = pygame.image.load(newpath)
            mask = pygame.mask.from_surface(surface)
            image = Image(surface, mask, path = str(path_obj))
            cls.cache[str(path_obj)] = image
            return image.rescale(scaling_width=scaling_width, scaling_height=scaling_height, scaling_factor=scaling_factor)

        # image gets loaded and preprocessed for the first (and only) time
        raw_image = pygame.image.load(str(path_obj))
        # If boundary is not black, remove it without losing pixels in the inside of the figure
        if colorkey != COLOR.BLACK: 
            temp = raw_image.copy()
            temp.set_colorkey(colorkey)
            # temp has now transparent boundary, but possibly also transparent pixels in the inside
            temp_mask = pygame.mask.from_surface(temp)
            temp_mask.invert() # the inverted mask covers all transparent pixels
            temp_mask = temp_mask.connected_component() # this component is exactly the boundary
            temp_mask.invert() # its inverse is the mask of the actual figure on the image
            alpha_surf = temp_mask.to_surface(setcolor=(255,255,255,255),
                                                      unsetcolor=(0,0,0,0))
            new_raw = pygame.Surface(raw_image.get_size(), pygame.SRCALPHA)
            new_raw.blit(raw_image, (0,0))
            new_raw.blit(alpha_surf, (0,0), special_flags=pygame.BLEND_RGBA_MULT)
            raw_image = new_raw # now its boundary is transparent
        bounding_rect = raw_image.get_bounding_rect()
        surface = pygame.Surface(bounding_rect.size, pygame.SRCALPHA)
        # surface now has its boundary trimmed to the smallest rectangle
        # containing the complete figure
        surface.blit(raw_image,(0,0),bounding_rect)
        mask = pygame.mask.from_surface(surface)
                
        # rescale image according to user's screen settings
        image = Image(surface, mask, path = str(path_obj)).rescale(scaling_width=scaling_width, scaling_height=scaling_height, scaling_factor=scaling_factor)
        # cache the result for quick access in the current game
        cls.cache[str(path_obj)] = image
        # and save it for the next execution of the game
        newpath.parent.mkdir(parents=True, exist_ok=True)
        pygame.image.save(image.surface, str(newpath))
        
        return image.rescale(scaling_width=scaling_width, scaling_height=scaling_height, scaling_factor=scaling_factor)

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
        N=ALIEN.BLOB.energy
        raw_blob = GraphicData(path = "images/alien/blob", scaling_width = ALIEN.BLOB.width)
        cls.blob = [raw_blob.frames[2].scale_by((N/n)**(-1/3)) for n in range(1,N//8)]+[raw_blob.frames[1].scale_by((N/n)**(-1/3)) for n in range(N//8,N//4+1)]+[raw_blob.frames[0].scale_by((N/n)**(-1/3)) for n in range(N//4+1, N+1)]
        raw_blubber = Image.load(path = f'images/bullet/blubber.png', scaling_width = BULLET.BLUBBER.width)
        cls.blubber = [raw_blubber.scale_by((N/n)**(-1/3)) for n in range(1,N+1)]
        cls.reflected_blubber = [cls.reflect(image, flip_x=True, flip_y=True) for image in cls.blubber]

@dataclass
class GraphicData:
    path: str | None = None
    image: Image | None = None
    frames: list[Image] | None = None
    colorkey: tuple = COLOR.BLACK
    scaling_width: int | None = None
    scaling_height: int | None = None
    scaling_factor: float | None = None
    animation_type: str | None = None
    fps: int | None = None
    animation_time: float | None = None
    frame_duration_ms: int | None = None
    starting_frame: int = 0

    def __post_init__(self):
        if not any([self.path, self.image, self.frames]):
            raise ValueError("GraphicData requires either path, image or frames.")
        if self.path is not None:
            # load image or frames, calculate remaining parameters
            path_obj = Path(self.path)
            if path_obj.is_dir():
                # load all images in the given directory
                image_paths = sorted([str(image_path) for image_path in path_obj.iterdir() if image_path.is_file()])
                self.frames = [Image.load(image_path, self.colorkey, self.scaling_width, self.scaling_height, self.scaling_factor) for image_path in image_paths]
                self.image = self.frames[self.starting_frame % len(self.frames)]
            else:
                self.image = Image.load(self.path, self.colorkey, self.scaling_width, self.scaling_height, self.scaling_factor)
                self.frames = [self.image]
        elif self.image is not None:
            self.path = self.image.path
            self.frames = [self.image]
        elif self.frames is not None:
            self.image = self.frames[self.starting_frame % len(self.frames)]
            self.path = str(Path(self.image.path).parent)
        if self.animation_type != "manual":
            if self.fps:
                self.animation_time = len(self.frames) / self.fps
                self.frame_duration_ms = int(1000 / self.fps)
            elif self.animation_time:
                self.fps = len(self.frames) / self.animation_time
                self.frame_duration_ms = int(self.animation_time * 1000 / len(self.frames))
            elif self.frame_duration_ms:
                self.animation_time = len(self.frames) * self.frame_duration_ms / 1000
                self.fps = len(self.frames) / self.animation_time