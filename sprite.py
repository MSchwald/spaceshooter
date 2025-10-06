import pygame
from settings import SCREEN
from image import Image, GraphicData
from display import Display
from math import hypot as norm
from math import sqrt, sin, cos, pi
from random import random, choice

class Sprite(pygame.sprite.Sprite):
    """Manage movement, boundary collision and animation of ingame objects"""
    def __init__(self, graphic: GraphicData,
                grid=None, center=None, x=0, y=0,
                direction=(0, 0), v=0, a=None,
                constraints=None, boundary_behaviour="clamp"):
        # Implemented boundary behaviours:
        #   clamp: sprite stops at the boundary (e.g. the ship)
        #   reflect: sprite gets reflected from the boundary
        #   vanish: sprite gets deleted when leaving the boundary (e.g. bullets)
        #   wrap: sprite reappears on the other side when leaving the boundary
        # Implemented animation types:
        #   None: non-animated Sprite
        #   loop: frames change periodically
        #   once: Sprite stays on the last frame after the animation
        #   vanish: Sprite gets removed after the animation
        #   pingpong: Sprite animated periodically back and forth
        #   random: frames get chosen randomly
        #   manual: Unused, no automatic frame update
        super().__init__()
        self.x, self.y = x, y
        self.graphic = graphic
        self.set_image(graphic.image)
        self.frame_number, self.frame_index = 0, graphic.starting_frame
        self.timer, self.timer_on_hold = 0, False
        if center:
            self.rect.center = center
            self.x, self.y = self.rect.x, self.rect.y
        elif grid:
            self.rect.center = ((grid[0]+1/2)*Display.grid_width,
                                (grid[1]+1/2)*Display.grid_width)
            self.x, self.y = self.rect.x, self.rect.y
        if direction == "random":
            angle = 2*pi*random()
            self.direction = (cos(angle),sin(angle))
        else:
            self.direction = direction
        self.v, self.a = v, a
        self.constraints, self.boundary_behaviour = constraints, boundary_behaviour
        
    def set_image(self, image):
        # initializes an image preserving (x,y) of the sprite
        self.image, self.surface, self.mask = image, image.surface, image.mask
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
        return self.v*self.direction[0]/self.norm

    @property
    def vy(self):
        if self.norm == 0:
            return 0
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
        # function could be removed
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
                #reflection only prevents exiting, not entering the constraints
                if (x - x_clamp) * self.direction[0] > 0:
                    self.x = 2*x_clamp - x
                    self.direction = (-self.direction[0], self.direction[1])
                else:
                    self.x = x_clamp
                if (y - y_clamp) * self.direction[1] > 0:
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
        """Calculate the state of the sprite after dt passed ms"""
        self.update_position(dt) # respects display settings, velocity and boundary behaviour 
        self.update_velocity(dt) # respects acceleration if available
        self.update_timer(dt) # respects possible timer pauses
        self.update_frame(dt) # respects animation if available

    def update_position(self, dt):
        self.change_position(self.x+dt*self.vx*Display.grid_width/SCREEN.GRID_WIDTH,
                            self.y+dt*self.vy*Display.grid_width/SCREEN.GRID_WIDTH)
    
    def update_velocity(self, dt):
        if self.a:
            self.direction = (self.vx+self.a[0]*dt,self.vy+self.a[1]*dt)
            self.v = norm(self.direction[0],self.direction[1])

    def update_timer(self, dt):
        if self.timer_on_hold == True:
            if self.pause_duration:
                self.pause_timer += dt
                if self.pause_timer > self.pause_duration:
                    self.timer_on_hold = False
        else:
            self.timer += dt
    
    def update_frame(self, dt):
        if self.timer_on_hold == False and self.graphic.animation_type not in (None, "manual"):
                new_index = self.new_frame_index()
                if new_index != self.frame_index:
                    self.frame_index = new_index
                    self.change_image(self.graphic.frames[self.frame_index])

    def new_frame_index(self):
        frame_number = self.timer // self.graphic.frame_duration_ms 
        if self.graphic.animation_type == "random":
            if frame_number > self.frame_number:
                self.frame_number = frame_number
                return choice(range(len(self.graphic.frames)))
            else:
                return self.frame_index
        else:
            self.frame_number = frame_number
            if self.graphic.animation_type == "vanish":
                if frame_number >= len(self.graphic.frames):
                    self.kill()
                    return self.frame_index
                else:
                    return frame_number
            elif self.graphic.animation_type == "pingpong":
                new_index = frame_number % (2*len(self.graphic.frames)-2)
                if new_index >= len(self.graphic.frames):
                    new_index = 2*(len(self.graphic.frames)-1) - new_index
                return new_index
            else:
                return {"loop": frame_number%len(self.graphic.frames),
                                    "once": min(frame_number, len(self.graphic.frames)-1)}[self.graphic.animation_type]

    def pause_for_ms(self, duration=None):
        self.timer_on_hold = True
        self.pause_timer = 0
        self.pause_duration = duration

    def reflect(self, flip_x=True, flip_y=True):
        self.direction = (-self.direction[0],-self.direction[1])
        self.graphic.frames = [Image.reflect(image, flip_x, flip_y) for image in self.graphic.frames]
        self.change_image(self.graphic.frames[self.frame_index])  

    def blit(self, screen):
        screen.blit(self.surface, self.rect)
