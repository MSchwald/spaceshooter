import pygame
from image import Image
from text import *
from settings import COLOR, SHIP, FONT
from display import Display

class Statusbar:
    """Format and render a two lined status bar with the relevant game stats"""
    initialized = False

    @classmethod
    def init(cls, level, rescaling = True):
        '''Load images and initialize fonts once'''
        if cls.initialized:
            return

        cls.rescaling = rescaling

        cls.empty_bar = pygame.image.load("images/statusbar/empty_bar.png").convert_alpha()
            
        cls.h = cls.empty_bar.get_height()
        cls.health = pygame.image.load("images/statusbar/health_bar.png").convert_alpha()
        cls.shield_timer = pygame.image.load("images/statusbar/shield_bar.png").convert_alpha()

        cls.font_size = cls.h*7//8
        cls.font = pygame.font.Font(FONT.STATS, cls.font_size)
        cls.stats_padding = (cls.h-cls.font_size)//2
            
        cls.lives_icon = pygame.image.load("images/statusbar/lives_icon.png").convert_alpha()
        cls.energy_icon = pygame.image.load("images/statusbar/energy_icon.png").convert_alpha()
        cls.shield_icon = pygame.image.load("images/statusbar/shield_icon.png").convert_alpha()     
        cls.missiles_icon = pygame.image.load("images/statusbar/missiles_icon.png").convert_alpha()

        cls.score_font_size = cls.font_size//2
        cls.score_font = pygame.font.Font(FONT.STATS, cls.score_font_size)
        cls.score_padding = (cls.h//2-cls.score_font_size)//2                

    @classmethod
    def blit(cls, level, screen = None):
        screen = screen or Display.screen
        if not cls.initialized:
            cls.init(level)
        cls.health_bar = cls.empty_bar.copy()
        cls.shield_bar = cls.empty_bar.copy()
        cls.health_bar.blit(cls.health, (19*cls.h//72,18*cls.h//72), area=(0,0,level.ship.energy*cls.health.get_width()//level.ship.max_energy,cls.h))
        cls.shield_bar.blit(cls.shield_timer, (19*cls.h//72,18*cls.h//72), area=(0,0,level.ship.shield_time*cls.shield_timer.get_width()//(1000*SHIP.MAX_SHIELD_DURATION),cls.h))   
        cls.missiles = pad_surface(cls.font.render(f"{level.ship.missiles%100:02d}", False, COLOR.WHITE), cls.stats_padding, vertical_padding=True, horizontal_padding=True)
        cls.level_number = pad_surface(cls.font.render(f"L{level.number%100:02d}", False, COLOR.WHITE), cls.stats_padding, vertical_padding=True, horizontal_padding=True)
        cls.lives = pad_surface(cls.font.render(f"{level.ship.lives%100:02d}", False, COLOR.WHITE), cls.stats_padding, vertical_padding=True, horizontal_padding=True)
        cls.first_row = align_surfaces([cls.level_number,cls.lives_icon,cls.lives,
                                        cls.energy_icon,cls.health_bar,cls.shield_icon,
                                        cls.shield_bar,cls.missiles_icon,cls.missiles],
                                        "horizontal", rescale_to_surface = cls.health_bar, spacing=cls.h//16)
        cls.score = cls.score_font.render(f"Score {int(level.ship.score)}", False, {False: COLOR.WHITE, True: COLOR.GREEN}[level.ship.score_factor > 1])
        cls.goal = cls.score_font.render(level.goal, False, COLOR.WHITE)
        cls.progress = cls.score_font.render(level.progress, False, COLOR.WHITE)
        cls.second_row = pygame.Surface((cls.first_row.get_width(),cls.score_font_size))
        cls.second_row.blit(cls.score,(0,0))
        cls.second_row.blit(cls.goal,((cls.first_row.get_width()-cls.goal.get_width())//2,0))
        cls.second_row.blit(cls.progress,(cls.first_row.get_width()-cls.progress.get_width(),0))
        cls.both_rows = align_surfaces([cls.first_row,cls.second_row], "vertical", spacing=cls.h//32)
        if cls.rescaling:
            cls.both_rows = pygame.transform.scale_by(cls.both_rows, Display.screen_width/cls.first_row.get_width())
        screen.blit(cls.both_rows,(0,0))