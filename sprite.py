from __future__ import annotations
import pygame
from settings import SCREEN
from display import Display
from image import Image, GraphicData
from timer import Timer, ActionTimer
from math import sqrt, sin, cos, pi
from random import random, choice
from physics import Vector, norm, Ball

class Sprite(pygame.sprite.Sprite):
    """Manage movement, boundary collision and animation of ingame objects.

    graphic: GraphicData, for visual representation of the sprite
        Implemented animation modes:
        - None – non-animated sprite
        - "loop" – frames cycle periodically
        - "once" – plays once, stops at last frame
        - "vanish" – disappears after animation completes
        - "pingpong" – alternates back and forth
        - "random" – frame indices are chosen randomly
        - "manual" – no automatic frame updates, handled externally
    pos, vel, acc: position, velocity and acceleration vectors (optional)
        - vel and acc are set to (0, 0) by default.
        - If no pos is provided, Sprite can be placed later using spawn(). 
    constraints, boundary_behaviour: pygame.Rect, str (optional)
        Movement area of the sprite and its interaction with its boundary.
        Implemented boundary behaviours:
        - None - no boundary restriction / interaction
        - "clamp" - stops at the boundary (the ship)
        - "reflect" - can enter its constraining area but is then confined
                    and bounces off the boundary (most enemies)
        - "vanish" - is removed when leaving the boundary (bullets, items)
        - "wrap" - reappears on the opposite side (enemies on starting screen)"""

    def __init__(self, graphic: GraphicData,
                pos: Vector | None = None,
                vel: Vector = Vector(0, 0),
                acc: Vector = Vector(0, 0),
                constraints: pygame.Rect | None = None,
                boundary_behaviour: str | None = None):
        super().__init__()
        self.pos, self.vel, self.acc = pos, vel, acc
        self.graphic = graphic
        self.frame_number, self.frame_index = 0, graphic.starting_frame
        self.animation_timer = ActionTimer(graphic.frame_duration_ms, cyclic = True)
        self.constraints, self.boundary_behaviour = constraints, boundary_behaviour
        self.rect = self.graphic.image.surface.get_rect()
        self.activated = False
        if pos is not None:
            self.spawn(pos = pos)

    def spawn(self, pos: Vector | None = None,
                    center: Vector | None = None,
                    grid: tuple[int, int] | None = None):
        """Spawn and activate sprite at a specified location.
        Exactly one of pos, center or grid must be provided."""
        if sum(arg is not None for arg in (pos, center, grid)) != 1:
            raise ValueError("Provide exactly one of pos, center or grid")
        if grid is not None:
            x, y = grid
            center = Vector(x + 0.5, y + 0.5) * Display.grid_width
        if center is not None:
            pos = center - Vector(self.w, self.h) / 2   
        self.activated = True    
        self.pos = pos  
        self.move_to(self.pos)

    # Short cuts for quick to access to graphical attributes
    @property
    def image(self) -> Image:
        return self.graphic.image

    @property
    def surface(self) -> pygame.Surface:
        return self.graphic.image.surface

    @property
    def mask(self) -> pygame.Mask:
        return self.graphic.image.mask

    @property
    def w(self) -> int:
        return self.image.w

    @property
    def h(self) -> int:
        return self.image.h

    # Various positional vectors
    @property
    def diag(self) -> Vector:
        return Vector(self.w, self.h)

    @property
    def center(self) -> Vector:
        if self.activated:
            return self.pos + self.diag / 2
        return Vector(self.rect.center)
        
    @property
    def midbottom(self) -> Vector:
        if self.activated:
            return self.pos + Vector(self.w / 2, self.h)
        return Vector(self.rect.midbottom)

    # Absolute speed calculated from the velocity vector
    @property
    def speed(self) -> int:
        return norm(self.vel)
 
    # Methods to change the visual representation of the Sprite
    def set_image(self, image: Image):
        """initializes an image preserving pos of the sprite"""
        self.graphic.image = image
        self.update_rect_size()
  
    def change_image(self, image: Image):
        """changes the image preserving the center of the sprite"""
        center = Vector(self.rect.centerx, self.rect.centery)
        self.set_image(image)
        self.move_to(center - self.diag / 2)

    def scale_image_by(self, factor: float):
        """rescales the image preserving the center of the sprite"""
        self.change_image(self.image.scale_by(factor))

    # The pygame.Rect attribute is needed for blitting the sprite,
    # should not be manipulated externally, only automatically
    # updated upon positional or graphical change of the sprite
    def update_rect_pos(self):
        self.rect.x, self.rect.y = int(self.pos.x), int(self.pos.y)

    def update_rect_size(self):
        self.rect.w, self.rect.h = int(self.w), int(self.h)

    def move_to(self, pos: Vector):
        """Move the sprite respecting its boundary behaviour."""
        if self.constraints is None or self.boundary_behaviour == "vanish":
            self.pos = pos
            self.update_rect_pos()
            if self.boundary_behaviour == "vanish" and not self.rect.colliderect(self.constraints):
                self.kill()
            return
        min_bound = Vector(self.constraints.x, self.constraints.y)
        max_bound = Vector(self.constraints.right, self.constraints.bottom)
        if self.boundary_behaviour == "clamp":
            self.pos = pos.clamp(min_bound, max_bound - self.diag)
        elif self.boundary_behaviour == "reflect":
            pos_clamp = pos.clamp(min_bound, max_bound - self.diag)
            diff = pos - pos_clamp

            #reflection only prevents exiting, not entering the constraints
            reflect_x = diff.x * self.vel.x > 0
            reflect_y = diff.y * self.vel.y > 0

            self.pos.x = 2 * pos_clamp.x - pos.x if reflect_x else pos_clamp.x
            self.pos.y = 2 * pos_clamp.y - pos.y if reflect_y else pos_clamp.y

            self.vel.x *= -1 if reflect_x else 1
            self.vel.y *= -1 if reflect_y else 1
                
        elif self.boundary_behaviour == "wrap":
            # wrapping happens when leaving the the constraints entirely
            pos_clamp = pos.clamp(min_bound - self.diag, max_bound)
            wrap_x = pos.x != pos_clamp.x
            wrap_y = pos.y != pos_clamp.y

            self.pos.x = self.constraints.right + self.constraints.x - self.w - pos.x if wrap_x else pos_clamp.x
            self.pos.y = self.constraints.bottom + self.constraints.y - self.h - pos.y if wrap_y else pos_clamp.y
        self.update_rect_pos()
        if self.boundary_behaviour == "vanish" and not self.rect.colliderect(self.constraints):
            self.kill()

    def update(self, dt: int):
        """Calculate the state of the sprite after dt passed ms"""
        if self.activated:
            self.update_vel(dt)
            self.update_pos(dt)
            self.animation_timer.update(dt)
            self.update_frame(dt)    

    def update_vel(self, dt: int):
        self.vel += dt * self.acc

    def update_pos(self, dt: int):
        self.move_to(self.pos + dt * self.vel * Display.grid_width / SCREEN.GRID_WIDTH)
    
    def update_frame(self, dt: int):
        """Update the Sprite's image to a new animation frame if needed."""
        if self.animation_timer.on_hold:
            return
        while self.animation_timer.check_alarm():
            self.next_frame()
            if self.frame_index is None:
                self.activated = False
                self.kill()
                return
            self.change_image(self.graphic.frames[self.frame_index])

    def next_frame(self):
        """Determine the next frame in the animation depending on provided animation type."""
        self.frame_number += 1
        match self.graphic.animation_type:
            case None: return
            case "random": self.frame_index = choice(range(len(self.graphic.frames)))
            case "vanish":
                if self.frame_number >= len(self.graphic.frames):
                    self.frame_index = None
                else:
                    self.frame_index = self.frame_number
            case "pingpong":
                self.frame_index = self.frame_number % (2*len(self.graphic.frames)-2)
                if self.frame_index >= len(self.graphic.frames):
                    self.frame_index = 2*(len(self.graphic.frames)-1) - self.frame_index
            case "loop": self.frame_index = self.frame_number % len(self.graphic.frames)
            case "once": self.frame_index = min(self.frame_number, len(self.graphic.frames)-1)

    def reflect(self, flip_x: bool, flip_y: bool):
        """Reflects direction of movement and all graphical data along given axes."""
        self.vel *= -1
        self.graphic.reflect(flip_x, flip_y)

    def blit(self, screen: pygame.Surface):
        """Blit the current state of the sürite onto the screen."""
        if self.activated:
            screen.blit(self.surface, self.rect)

    @property
    def ball(self) -> Ball:
        """Aproximate the sprite with a 3d ball of the same width."""
        return Ball(self.center, self.vel, self.w / 2)