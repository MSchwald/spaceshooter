import pygame, settings
from numpy.linalg import norm
from math import sin, cos, pi
from random import random
from image import Image


class Sprite(pygame.sprite.Sprite):
    # class for all sprites
    def __init__(self, image, grid=None, center=None, x=0, y=0, v=0, direction=(0, 0), constraints=None, boundary_behaviour="clamp"):
        # possible boundary behaviours:
        #   clamp: sprite stops at the boundary (e.g. the ship)
        #   reflect: sprite gets reflected from the boundary
        #   vanish: sprite gets deleted when leaving the boundary (e.g. bullets)
        #   wrap: sprite reappears on the other side when leaving the boundary
        super().__init__()
        self.x = x
        self.y = y
        self.set_image(image)
        if center:
            self.rect.center = center
            self.x = self.rect.x
            self.y = self.rect.y
        elif grid:
            self.rect.center = ((grid[0]+1/2)*settings.grid_width,(grid[1]+1/2)*settings.grid_width)
            self.x = self.rect.x
            self.y = self.rect.y
        self.v = v
        if direction == "random":
            angle = 2*pi*random()
            self.direction = (cos(angle),sin(angle))
        else:
            self.direction = direction
        self.constraints = constraints
        self.boundary_behaviour = boundary_behaviour
        self._norm = norm(self.direction)
        
    def set_image(self, image):
        # initializes an image preserving (x,y) of the sprite
        self.image = image
        self.surface = image.surface
        self.mask = image.mask
        self.rect = pygame.Rect(int(self.x), int(self.y), self.w, self.h)

    @property
    def w(self):
        return self.image.w

    @property
    def h(self):
        return self.image.h
        
    def change_image(self, image):
        # changes the image preserving the center of the sprite
        center = self.rect.center
        self.set_image(image)
        self.rect.center = center
        self.change_position(self.rect.x, self.rect.y)

    def scale_image_by(self, factor):
        # rescales the image preserving the center of the sprite
        self.change_image(self.image.scale_by(factor))

    def change_direction(self, x, y):
        self.direction = (x, y)
        self._norm = norm(self.direction)

    def turn_direction(self, phi):
        """turns the direction of the sprite counter-clockwise, angle measured in radians"""
        self.change_direction(self.direction[0]*cos(phi)+self.direction[1]*sin(
            phi), -self.direction[0]*sin(phi)+self.direction[1]*cos(phi))

    def change_position(self, x, y):
        if self.constraints is None or self.boundary_behaviour == "vanish":
            self.x, self.y = x, y
        elif self.boundary_behaviour in ["clamp", "reflect"]:
            x_clamp = min(max(x, self.constraints.x),
                          self.constraints.right-self.w)
            y_clamp = min(max(y, self.constraints.y),
                          self.constraints.bottom-self.h)
            if self.boundary_behaviour == "reflect":
                if x != x_clamp:
                    self.x = 2*x_clamp-x
                    self.direction = (-self.direction[0],self.direction[1])
                else:
                    self.x = x_clamp
                if y != y_clamp:
                    self.y = 2*y_clamp-y
                    self.direction = (self.direction[0],-self.direction[1])
                else:
                    self.y = y_clamp
            else:
                self.x, self.y = x_clamp, y_clamp
        elif self.boundary_behaviour == "wrap":
            x_clamp = min(max(x, self.constraints.x-self.w),
                          self.constraints.right)
            y_clamp = min(max(y, self.constraints.y-self.h),
                          self.constraints.bottom)
            if x != x_clamp:
                self.x = self.constraints.right+self.constraints.x-self.w-x
            else:
                self.x = x_clamp
            if y != y_clamp:
                self.y = self.constraints.bottom+self.constraints.y-self.h-y
            else:
                self.y = y_clamp
        self.rect.x, self.rect.y = int(self.x), int(self.y)
        if self.boundary_behaviour == "vanish" and not self.rect.colliderect(self.constraints):
            self.kill()

    def update(self, dt):
        if self._norm != 0 and self.v != 0:
            newx = self.x+dt*self.v*self.direction[0]/self._norm
            newy = self.y+dt*self.v*self.direction[1]/self._norm
            self.change_position(newx, newy)

    def blit(self, screen):
        screen.blit(self.surface, self.rect)
