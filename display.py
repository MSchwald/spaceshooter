import pygame, settings

class Display:
    # Go into fullscreen mode with the current display settings of the player
    def __init__(self):
        pygame.display.init()
        self.info = pygame.display.Info()
        self.width, self.height = self.info.current_w, self.info.current_h
        self.display = pygame.display.set_mode((self.width, self.height), pygame.FULLSCREEN)

    def get_game_surface_with_ratio(self,w,h):
        #Fix a maximal surface "screen" on the display with following width:height ratio
        ratio = h*self.width-w*self.height

        if ratio == 0:
            # display has the desired ratio, no padding necessary
            screen_w,screen_h = (self.width,self.height)
            Display.padding_w, Display.padding_h = (0,0)  
        elif ratio > 0:
            # display is too wide
            screen_w, screen_h = w * self.height // h, self.height
            Display.padding_w, Display.padding_h = (self.width - screen_w) // 2, 0
        else:
            # display is too high
            screen_w, screen_h = self.width, self.width * h // w
            Display.padding_w, Display.padding_h = 0, (self.height - screen_h) // 2

        self.screen = pygame.Surface((screen_w,screen_h))
        self.screen_rect = pygame.Rect(Display.padding_w,Display.padding_h,screen_w,screen_h)
        Display.screen_width = self.screen.get_width()
        Display.screen_height = self.screen.get_height()
        Display.grid_width = Display.screen_width // settings.grid[0]
        return self.screen

    def update(self, padding_color):
        """blits screen centered on display,
        padding visible if screen ratio is not as fixed
        in the settings"""
        self.display.fill(padding_color)
        self.display.blit(self.screen,self.screen_rect)
        pygame.display.flip()

