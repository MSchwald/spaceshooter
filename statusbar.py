import pygame, settings
from image import Image
from text import *
from settings import color
from display import Display

class Statusbar:
    '''Class to format a two lined status bar
    out of the most importantstats in the game'''
    def __init__(self, level, rescaling = True):
            
            self.level = level
            self.rescaling = rescaling

            self.empty_bar = pygame.image.load("images/statusbar/empty_bar.png").convert_alpha()
            
            self.h = self.empty_bar.get_height()
            self.health = pygame.image.load("images/statusbar/health_bar.png").convert_alpha()
            self.shield_timer = pygame.image.load("images/statusbar/shield_bar.png").convert_alpha()

            self.font_size = self.h*7//8
            self.font = pygame.font.Font(settings.stats_font, self.font_size)
            self.stats_padding = (self.h-self.font_size)//2
            
            self.lives_icon = pygame.image.load("images/statusbar/lives_icon.png").convert_alpha()
            self.energy_icon = pygame.image.load("images/statusbar/energy_icon.png").convert_alpha()
            self.shield_icon = pygame.image.load("images/statusbar/shield_icon.png").convert_alpha()     
            self.missiles_icon = pygame.image.load("images/statusbar/missiles_icon.png").convert_alpha()

            self.score_font_size = self.font_size//2
            self.score_font = pygame.font.Font(settings.stats_font, self.score_font_size)
            self.score_padding = (self.h//2-self.score_font_size)//2                

    def blit(self, screen):
        self.health_bar = self.empty_bar.copy()
        self.shield_bar = self.empty_bar.copy()
        self.health_bar.blit(self.health, (19*self.h/72,18*self.h/72), area=(0,0,self.level.ship.energy/self.level.ship.max_energy*self.health.get_width(),self.h))
        self.shield_bar.blit(self.shield_timer, (19*self.h/72,18*self.h/72), area=(0,0,self.level.ship.shield_timer/(1000*settings.max_shield_duration)*self.shield_timer.get_width(),self.h))   
        self.missiles = pad_surface(self.font.render(f"{self.level.ship.missiles%100:02d}", False, color["white"]), self.stats_padding, vertical_padding=True, horizontal_padding=True)
        self.level_number = pad_surface(self.font.render(f"L{self.level.number%100:02d}", False, color["white"]), self.stats_padding, vertical_padding=True, horizontal_padding=True)
        self.lives = pad_surface(self.font.render(f"{self.level.ship.lives%100:02d}", False, color["white"]), self.stats_padding, vertical_padding=True, horizontal_padding=True)
        self.first_row = align_surfaces([self.level_number,self.lives_icon,self.lives,
                                        self.energy_icon,self.health_bar,self.shield_icon,
                                        self.shield_bar,self.missiles_icon,self.missiles],
                                        "horizontal", rescale_to_surface = self.health_bar, spacing=self.h//16)
        self.score = self.score_font.render(f"Score {int(self.level.ship.score)}", False, {False: color["white"], True: color["green"]}[self.level.ship.score_factor > 1])
        self.goal = self.score_font.render(self.level.goal, False, color["white"])
        self.progress = self.score_font.render(self.level.progress, False, color["white"])
        self.second_row = pygame.Surface((self.first_row.get_width(),self.score_font_size))
        self.second_row.blit(self.score,(0,0))
        self.second_row.blit(self.goal,((self.first_row.get_width()-self.goal.get_width())/2,0))
        self.second_row.blit(self.progress,(self.first_row.get_width()-self.progress.get_width(),0))
        self.both_rows = align_surfaces([self.first_row,self.second_row], "vertical", spacing=self.h/32)
        if self.rescaling:
            self.both_rows = pygame.transform.scale_by(self.both_rows, Display.screen_width/self.first_row.get_width())
        screen.blit(self.both_rows,(0,0))