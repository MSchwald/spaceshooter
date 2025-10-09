from __future__ import annotations
import pygame
from pathlib import Path
from display import Display
from settings import COLOR, SCREEN, ITEM, ALIEN, SHIP, BULLET
from dataclasses import dataclass

class Image:
    '''Manage lazy loading and transforming images and masks to be used for sprites'''
    def __init__(self, surface: pygame.Surface,
                    mask: pygame.Mask,
                    colorkey: tuple = None,
                    reflected: bool = False,
                    path: str | None = None):
        self.surface = surface
        self.mask = mask
        self.path = path
        if colorkey:
            self.surface.set_colorkey(colorkey)

    @property
    def rect(self) -> pygame.Rect:
        return self.surface.get_rect()
    
    @property
    def w(self) -> int:
        return self.rect.w
    
    @property
    def h(self) -> int:
        return self.rect.h

    def scale_by(self, factor: float) -> Image:
        '''Rescale image and its mask by a given factor'''
        return Image(pygame.transform.scale(self.surface, (factor*self.w, factor*self.h)).convert_alpha(),
            self.mask.scale((factor*self.w, factor*self.h)))

    def rescale(self, scaling_width: float = None,
                    scaling_height: float = None,
                    scaling_factor: float = None):
        '''Rescaling image either to a given width, height or by a factor'''
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

    cache = {}
    @classmethod
    def load(cls, path, colorkey=COLOR.BLACK, scaling_width=None, scaling_height=None, scaling_factor=None) -> Image:
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

        image = Image.preprocess(str(path_obj), colorkey=colorkey, scaling_width=scaling_width, scaling_height=scaling_height, scaling_factor=scaling_factor)
        # cache the preprocessed image for quick access in the current game
        cls.cache[str(path_obj)] = image
        # and save it for the next execution of the game
        newpath.parent.mkdir(parents = True, exist_ok = True)
        pygame.image.save(image.surface, str(newpath))
        
        return image.rescale(scaling_width=scaling_width, scaling_height=scaling_height, scaling_factor=scaling_factor)

    @classmethod
    def preprocess(cls, path: str,
                    colorkey: tuple = COLOR.BLACK,
                    scaling_width: float | None = None,
                    scaling_height: float | None = None,
                    scaling_factor: float | None = None) -> Image:
        raw_surface = pygame.image.load(path)
        cropped_surface = Image.crop_boundary(raw_surface, colorkey)
        mask = pygame.mask.from_surface(cropped_surface)
        return Image(cropped_surface, mask, path = path).rescale(scaling_width=scaling_width, scaling_height=scaling_height, scaling_factor=scaling_factor)

    @classmethod
    def crop_boundary(cls, surface: pygame.Surface, colorkey: tuple = COLOR.BLACK) -> pygame.Surface:
        """Remove boundary of given colorkey from surface"""
        temp = surface.copy()
        # If boundary is not black, remove it without losing pixels in the inside of the figure
        if colorkey != COLOR.BLACK: 
            temp.set_colorkey(colorkey)
            # temp has now transparent boundary, but possibly also transparent pixels in the inside
            temp_mask = pygame.mask.from_surface(temp)
            temp_mask.invert() # the inverted mask covers all transparent pixels
            temp_mask = temp_mask.connected_component() # this component is exactly the boundary
            temp_mask.invert() # its inverse is the mask of the actual figure on the image
            alpha_surf = temp_mask.to_surface(setcolor=(255,255,255,255),
                                                      unsetcolor=(0,0,0,0))
            new_raw = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
            new_raw.blit(surface, (0,0))
            new_raw.blit(alpha_surf, (0,0), special_flags=pygame.BLEND_RGBA_MULT)
            temp = new_raw # now its boundary is transparent
        bounding_rect = temp.get_bounding_rect()
        cropped_surface =  pygame.Surface(bounding_rect.size, pygame.SRCALPHA)
        cropped_surface.blit(temp, (0,0), bounding_rect)
        return cropped_surface

    reflected_cache = {}
    @classmethod
    def reflect(cls, image: Image, flip_x: bool, flip_y: bool) -> Image:
        if not (flip_x or flip_y):
            return image
        if (image.path, image.w, image.h, flip_x, flip_y) in cls.reflected_cache.keys():
            return cls.reflected_cache[(image.path, image.w, image.h, flip_x, flip_y)]
        flipped_surface = pygame.transform.flip(image.surface, flip_x=flip_x, flip_y=flip_y)
        flipped_image = Image(flipped_surface, pygame.mask.from_surface(flipped_surface), path = image.path)
        cls.reflected_cache[(image.path, image.w, image.h, flip_x, flip_y)] = flipped_image
        return flipped_image            

    def blit(self, screen: pygame.Surface):
        screen.blit(self.surface, self.rect, colorkey=self.surface.get_colorkey())

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
        if sum(arg is not None for arg in (self.path, self.image, self.frames)) != 1:
            raise ValueError("Provide exactly one of path, image or frames.")
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

    def reflect(self, flip_x: bool, flip_y: bool):
        self.image = Image.reflect(self.image, flip_x, flip_y)
        self.frames = [Image.reflect(frame, flip_x, flip_y) for frame in self.frames]