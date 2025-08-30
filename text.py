import pygame
from pygame.locals import *
import settings


class Font():
    """Initializes the fonts used in the game"""

    def __init__(self):
        self.stats = pygame.font.Font(settings.stats_font, 30)
        self.menu = pygame.font.Font(settings.menu_font, 30)
        self.text = pygame.font.Font(settings.text_font, 30)


class Menu():
    """Class to create menus with a given title message and a given list of options"""

    def __init__(self, font, message=["Press Return to continue."], options=["Continue"], current_selection=0):
        self.font = font
        self.message = message
        self.options = options
        self.current_selection = current_selection
        self.number_of_lines = len(message)+len(options)
        self.lines = {}
        self.active_lines = {}
        for i in range(len(message)):
            # Renders each line of the title message
            self.lines[i] = self.font.text.render(
                message[i], False, (255, 255, 255))
        for j in range(len(options)):
            # Renders each of the options, inactive and active
            self.lines[len(message)+j] = self.font.menu.render(options[j],
                                                               False, (200, 200, 255), (0, 0, 255))
            self.active_lines[j] = self.font.menu.render(
                options[j], False, (255, 255, 0), (100, 100, 100))
        # Calculates size of the menu
        self.line_height = max(line.get_height()
                               for line in self.lines.values())
        self.line_length = max(line.get_width()
                               for line in self.lines.values())
        self.h = 2*settings.menu_boundary + self.number_of_lines * \
            (self.line_height+settings.line_distance) + \
            settings.title_menu_distance - settings.line_distance
        self.w = 2*settings.menu_boundary + self.line_length
        # Blit all the lines on a blue rectangle
        self.surface = pygame.Surface((self.w, self.h))
        self.surface.fill((0, 0, 255))
        for i in range(len(message)):
            self.surface.blit(self.lines[i], (settings.menu_boundary,
                              settings.menu_boundary+i*(self.line_height+settings.line_distance)))
        for i in range(len(message), self.number_of_lines):
            self.surface.blit(self.lines[i], ((self.w-self.lines[i].get_width(
            ))/2, settings.title_menu_distance+settings.menu_boundary+i*(self.line_height+settings.line_distance)))
        # Create a surface for each possible highlighted option
        self.surface_highlighted = {}
        for j in range(len(self.options)):
            self.surface_highlighted[j] = self.surface.copy()
            self.surface_highlighted[j].blit(self.active_lines[j], ((self.w-self.active_lines[j].get_width(
            ))/2, settings.title_menu_distance+settings.menu_boundary+(len(message)+j)*(self.line_height+settings.line_distance)))

    def move_selection(self, event_key):
        """Navigate through the menu"""
        if event_key == K_w:
            self.current_selection = (
                self.current_selection - 1) % len(self.options)
        if event_key == K_s:
            self.current_selection = (
                self.current_selection + 1) % len(self.options)

    def select(self):
        return self.options[self.current_selection]

    def blit(self, screen):
        """blits the menu with the current selection highlighted"""
        screen.blit(self.surface_highlighted[self.current_selection], ((
            screen.get_width()-self.w)/2, (screen.get_height()-self.h)/2))
