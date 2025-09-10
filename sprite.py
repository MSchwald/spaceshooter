import pygame, settings
from math import sin, cos, pi
from random import random
from image import Image
#from numpy.linalg import norm
from math import hypot as norm
from random import choice
from math import sqrt

class Sprite(pygame.sprite.Sprite):
    # class for all sprites
    def __init__(self, image=None, grid=None, center=None, x=0, y=0, v=0, direction=(0, 0), constraints=None, boundary_behaviour="clamp", animation_type=None, frames=None, fps=None, animation_time=None, starting_frame=0):
        #Non-animated sprites should have an Image-object as 'image',
        #   animated sprites only need a list 'frames' of Image-objects and start on frame 0
        # possible boundary behaviours:
        #   clamp: sprite stops at the boundary (e.g. the ship)
        #   reflect: sprite gets reflected from the boundary
        #   vanish: sprite gets deleted when leaving the boundary (e.g. bullets)
        #   wrap: sprite reappears on the other side when leaving the boundary
        #possible animation types:
        #   None: non-animated Sprite
        #   loop: frames change periodically
        #   once: Sprite stays on the last frame after the animation
        #   vanish: Sprite gets removed after the animation
        #   pingpong: Sprite animated periodically back and forth
        #   random: frames get chosen randomly
        #frames expects a list of Image-objects, the speed of the animation can
        #   either be specified via fps or animation_time (in seconds)
        super().__init__()
        self.x = x
        self.y = y
        self.animation_type = animation_type
        self.frames = frames
        if animation_type is None:
            self.set_image(image)
        else:
            self.set_image(frames[starting_frame])
            self.frame_number = 0
            self.frame_index = starting_frame
            if animation_type != "manual":
                if fps:
                    self.frame_duration_ms = int(1/fps*1000)
                elif animation_time:
                    self.frame_duration_ms = int(animation_time*1000/len(frames))
        self.timer = 0
        self.timer_on_hold = False
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
        
    def set_image(self, image):
        # initializes an image preserving (x,y) of the sprite
        self.image = image
        self.surface = image.surface
        self.mask = image.mask
        self.rect = pygame.Rect(int(self.x), int(self.y), image.w, image.h)

    @property
    def w(self):
        return self.image.w

    @property
    def h(self):
        return self.image.h

    @property
    def norm(self):
        return norm(self.direction[0],self.direction[1])

    @property
    def vx(self):
        if self.norm == 0:
            return 0
        else:
            return self.v*self.direction[0]/self.norm

    @property
    def vy(self):
        if self.norm == 0:
            return 0
        else:
            return self.v*self.direction[1]/self.norm
  
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
        # speed of sprites gets automatically rescaled by the grid_width
        self.update_position(dt)
        self.update_timer(dt)
        self.update_frame(dt)

    def update_position(self, dt):
        self.change_position(self.x+dt*self.vx*settings.grid_width/100, self.y+dt*self.vy*settings.grid_width/100)
        
    def update_timer(self, dt):
        if self.timer_on_hold == True:
            if self.pause_duration:
                self.pause_timer += dt
                if self.pause_timer > self.pause_duration:
                    self.timer_on_hold = False
        else:
            self.timer += dt
    
    def update_frame(self, dt):
        if self.timer_on_hold == False and self.animation_type and self.animation_type != "manual" :
                new_index = self.new_frame_index()
                if new_index != self.frame_index:
                    self.frame_index = new_index
                    self.change_image(self.frames[self.frame_index])

    def new_frame_index(self):
        frame_number = self.timer//self.frame_duration_ms 
        if self.animation_type == "random":
            if frame_number > self.frame_number:
                self.frame_number = frame_number
                return choice(range(len(self.frames)))
            else:
                return self.frame_index
        else:
            self.frame_number = frame_number
            if self.animation_type == "vanish":
                if frame_number >= len(self.frames):
                    self.kill()
                else:
                    return frame_number
            elif self.animation_type == "pingpong":
                new_index = frame_number % (2*len(self.frames)-2)
                if new_index >= len(self.frames):
                    new_index = 2*(len(self.frames)-1) - new_index
                return new_index
            else:
                return {"loop": frame_number%len(self.frames),
                                    "once": min(frame_number, len(self.frames)-1)}[self.animation_type]

    def pause_for_ms(self, time=None):
        self.timer_on_hold = True
        self.pause_timer = 0
        self.pause_duration = time

    def reflect(self, flip_x=True, flip_y=True):
        self.direction = (-self.direction[0],-self.direction[1])
        self.image = Image.reflect(self.image, flip_x, flip_y)
        if self.frames:
            self.frames = [Image.reflect(image, flip_x, flip_y) for image in self.frames]
            self.change_image(self.frames[self.frame_index])  

    def blit(self, screen):
        screen.blit(self.surface, self.rect)
