import pygame
from pygame.locals import *
import settings
from alien import Alien,blob_images
from level import Level
from menu import *
from image import Image
from random import random, choice
from item import Item
from sprite import Sprite
from statusbar import Statusbar
import sound
from pathlib import Path
import json,string
from screen import display_size, screen, screen_rect
from highscores import Highscores


class Game:
    """Overall class to manage the games logic and updating the screen """

    def __init__(self):
        """Initialize the game and starting stats"""

        pygame.init()

        # Fixes the maximal screen on the display with 16:9 ratio
        self.display = pygame.display.set_mode(display_size, pygame.FULLSCREEN)
        self.screen = screen #The game's surface

        self.player_name = ""
        self.level = Level(0)
        self.highscores = Highscores()
        self.statusbar = Statusbar(self.level)
        self.clock = pygame.time.Clock()

    def run(self):
        """Starts the main loop for the game."""
        self.running = True  # checks if the game gets shut down
        self.mode = "menu"  # possible modes: "game", "menu", "enter name" (for highscores)
        self.active_menu = Menu.make_main_menu(self)
        self.level.start()

        #main loop of the game
        while self.running:
            # 1) handle keyboard and mouse input
            self.handle_events()

            # measures passed time and limits the frame rate to 60fps
            dt = self.clock.tick(60)
            
            # 2) run the game for dt milliseconds (pauses if in menu mode)
            if self.mode == "game" or self.level.status == "start":
                self.level.update(dt) # update all ingame objects according to the passed time
                self.update_menu_status() # open a menu if necessary

            # 3) show the new frame of the game on the screen 
            self.render_screen()
        pygame.quit()

    def handle_events(self):
        """handle keyboard and mouse events"""
        for event in pygame.event.get():

            # The 'X' of the window and ESCAPE end the game
            if event.type == pygame.QUIT:
                self.running = False
                break
            if event.type == KEYDOWN and event.key == K_ESCAPE:
                self.running = False
                break

            # Controls in game mode
            if self.mode == "game":
                if event.type == KEYDOWN:
                    # RETURN pauses the game and opens the pause menu
                    if event.key == K_RETURN:
                        self.mode = "menu"
                        self.active_menu = Menu.make_main_menu(self)
                        break
                    # SPACE shoots bullets
                    elif event.key == K_SPACE:
                        self.level.ship.shoot_bullets()
                    elif event.key == K_LSHIFT:
                        self.level.ship.activate_shield()
                if event.type == KEYUP and event.key == K_LSHIFT:
                    self.level.ship.deactivate_shield()
                if event.type == MOUSEBUTTONDOWN and event.button == 1:
                    x,y = event.pos
                    self.level.ship.shoot_missile(x,y)

            #Enter the name into the high score table
            if self.mode == "enter name":
                self.highscores.update_name(name=self.player_name, rank=self.score_rank)
                self.active_menu = Menu.make_highscores_menu(message=["Congratulations!", f"Your score ranks on place {self.score_rank+1}.", "Please enter your name and press RETURN."], options=[f"Name: {self.player_name}"], highscores = self.highscores)
                if event.type == KEYDOWN:
                    if event.unicode in self.highscores.allowed_chars and len(self.player_name)<=10:
                        self.player_name += event.unicode
                    elif event.key == K_BACKSPACE:
                        self.player_name = self.player_name[:-1]
                    elif event.key == K_RETURN:
                        self.highscores.save()
                        self.active_menu = Menu.make_main_menu(self)
                        self.mode = "menu"
                        self.render_screen()
                        continue
                    
            # Navigating the menu
            if self.mode == "menu":
                if event.type == KEYDOWN:
                    if event.key in [K_w, K_s]:
                        self.active_menu.move_selection(event.key)
                    if event.key == K_RETURN:
                        Menu.choose_current_selection(self)

    # set the direction of the ship according to keyboard input
        if self.level.status != "start":
            keys = pygame.key.get_pressed()
            self.level.ship.control(keys)   

    def update_menu_status(self):
        """Check if the current level is solved or the player is game over"""
        if self.level.status in ["level_solved", "game_won", "game_over"]:
            self.level.play_status_sound()
            self.mode = "menu"
            if self.level.status == "level_solved":
                self.active_menu = Menu(message=[f"Level {self.level.number} solved!", f"In level {self.level.number+1}, you have to", f"{Level.goal[self.level.number+1]}"],
                options=["Next level"])
            else:
                self.active_menu = {"game_won": game_won_menu,
                                    "game_over":game_over_menu}[self.level.status]


    def render_screen(self):
        """Blit all sprites, stats, menu etc onto the display in the correct order"""
        self.display.fill((50,50,50)) # padding visible if screen ratio is not 16:9
        self.screen.fill(settings.bg_color) # background

        self.statusbar.blit(self.screen) # game stats
        self.level.blit(self.screen) # ship, enemies, items, bullets, crosshairs

        if self.mode == "menu" or self.mode == "enter name":
            self.active_menu.blit(self.screen)

        self.display.blit(self.screen,screen_rect)
        pygame.display.flip()