import pygame
from pygame.locals import *
import settings
from alien import Alien,blob_images
from level import Level
from text import *
from image import Image
from random import random, choice
from item import Item
from sprite import Sprite
from statusbar import Statusbar
import sound
from pathlib import Path
import json,string
from screen import display_size, screen, screen_rect


class Game:
    """Overall class to manage the games logic and updating the screen """

    def __init__(self):
        """Initialize the game and starting stats"""

        pygame.init()

        # Fixes the maximal screen on the display with 16:9 ratio
        self.display = pygame.display.set_mode(display_size, pygame.FULLSCREEN)
        self.screen = screen #The game's surface

        # Load high scores or use the default ones from the settings
        try:
            with open("highscores.json", "r", encoding="utf-8") as f:
                self.highscores = json.load(f)
        except FileNotFoundError:
            if settings.default_highscores:
                self.highscores = sorted(settings.default_highscores, key=lambda x: x[1], reverse=True)[:settings.max_number_of_highscores]
        self.allowed_chars = string.ascii_letters + string.digits #allowed characters in the table

        self.level = Level(0)
        self.statusbar = Statusbar(self.level)
        self.clock = pygame.time.Clock()

    def run(self):
        """Starts the main loop for the game."""
        self.running = True  # checks if the game gets shut down
        self.mode = "menu"  # possible modes: "game", "menu", "enter name" (for highscores)
        self.active_menu = main_menu
        self.level.start()

        #main loop of the game
        while self.running:
            # 1) handle keyboard and mouse input
            self.handle_events()

            # measures passed time and limits the frame rate to 60fps
            dt = self.clock.tick(60)
            
            # 2) run the game for dt milliseconds (pauses if in menu mode)
            if self.mode == "game":
                self.level.update(dt) # update all ingame objects according to the passed time

            # 3) show the new frame of the game on the screen 
            self.update_screen()
        pygame.quit()

    def handle_events(self):
        """handle the event queue"""
        for event in pygame.event.get():

            # Clicking the 'X' of the window ends the game
            if event.type == pygame.QUIT:
                self.running = False
                break
            # ESC ends the game
            if event.type == KEYDOWN and event.key == K_ESCAPE:
                self.running = False
                break
            # Controls in game mode
            if self.mode == "game":
                if event.type == KEYDOWN:
                    # RETURN pauses the game and opens the main menu
                    if event.key == K_RETURN:
                        self.mode = "menu"
                        self.active_menu = pause_menu
                        break
                    # SPACE shoots bullets
                    elif event.key == K_SPACE:
                        self.level.ship.shoot_bullets()
                    # Keys to test the different ship-levels, only for beta-version
                    #elif event.key == K_1:
                    #    self.level.ship.set_rank(1)
                    #elif event.key == K_2:
                    #    self.level.ship.set_rank(2)
                    #elif event.key == K_3:
                    #    self.level.ship.set_rank(3)
                    elif event.key == K_LSHIFT:
                        self.level.ship.activate_shield()
                if event.type == KEYUP and event.key == K_LSHIFT:
                    self.level.ship.deactivate_shield()
                if event.type == MOUSEBUTTONDOWN and event.button == 1:
                    x,y = event.pos
                    self.level.ship.shoot_missile(x,y)

            #Enter the name into the high score table
            if self.mode == "enter name":
                self.active_menu = Menu(message=["Congratulations!", "You achieved a new high score.", "Please enter your name and press RETURN."], options=[str(score[0]) + " " + str(score[1]) for score in self.highscores], current_selection=self.highscore_place)
                if event.type == KEYDOWN:
                    if event.key == K_BACKSPACE:
                        self.highscores[self.highscore_place][0] = self.highscores[self.highscore_place][0][:-1]
                    if event.key == K_RETURN:
                        with open("highscores.json", "w", encoding="utf-8") as f:
                            json.dump(self.highscores,f)
                        self.active_menu = highscores_checked
                        self.mode = "menu"
                    elif event.unicode in self.allowed_chars and len(self.highscores[self.highscore_place][0])<10:
                        self.highscores[self.highscore_place][0] += event.unicode
            
            # Navigating the menu
            if self.mode == "menu":
                if event.type == KEYDOWN:
                    if event.key in [K_w, K_s]:
                        self.active_menu.move_selection(event.key)
                    if event.key == K_RETURN:
                        selection = self.active_menu.select()
                        if selection in ["Restart","Start game"]:
                            self.mode = "game"
                            self.level.restart()
                        elif selection == "Exit":
                            self.running = False
                            break
                        elif selection == "Continue":
                            self.mode = "game"
                            if self.active_menu == level_solved_menu:
                                self.level.next()
                        elif selection == "Highscores":
                            self.active_menu = Menu(message=["Highscores", "Do you think you can beat them?", ""]+[str(score[0]) + " " + str(score[1]) for score in self.highscores], options=["Go back"])
                        elif selection == "Go back":
                            self.active_menu = main_menu
                        elif selection == "Buy Premium":
                            self.active_menu = premium_menu
                        elif selection == "Credits":
                            self.active_menu = credits_menu
                        elif selection == "Check high scores":
                            if len(self.highscores) < settings.max_number_of_highscores or self.level.ship.score > self.highscores[-1][1]:
                                pygame.mixer.stop()
                                sound.new_highscore.play()
                                self.highscore_place = [i for i in range(len(self.highscores)) if self.highscores[i][1]<self.level.ship.score][0]
                                self.highscores.append(["", self.level.ship.score])
                                self.highscores = sorted(self.highscores, key=lambda x: x[1], reverse=True)[:settings.max_number_of_highscores]
                                self.mode = "enter name"
                            else:
                                self.active_menu = Menu(message=["No new high score!", "Your score was too low,", "maybe next time!", ""]+[str(score[0]) + " " + str(score[1]) for score in self.highscores], options=["OK"])
                        else:
                            self.active_menu = highscores_checked

    # set the direction of the ship according to keyboard input
        keys = pygame.key.get_pressed()
        self.level.ship.control(keys)   

    def update_menu_status(self):
        """Check if the current level is solved or the player is game over"""
        if self.mode == "game" and self.level.status() != "running":
            self.level.play_status_sound()
            self.mode = "menu"
            self.active_menu ={"level_solved": level_solved_menu,
                                "game_won":game_won_menu,
                                "game_over":game_over_menu}[self.level.status()]


    def update_screen(self):
        """Updates screen with all sprites and stats"""
        self.display.fill((50,50,50)) #padding visible if screen ratio is not 16:9
        self.screen.fill(settings.bg_color) #background

        self.statusbar.blit(self.screen)
        self.blit_sprites() #ship, enemies, items, bullets

        self.level.crosshairs.blit(self.screen)

        self.update_menu_status() # open a menu if necessary
        if self.mode == "menu" or self.mode == "enter name":
            self.active_menu.blit(self.screen)

        self.display.blit(self.screen,screen_rect)

        # display the new screen
        pygame.display.flip()

    def blit_sprites(self):
        """blit the updated sprites"""
        for bullet in self.level.bullets:
            bullet.blit(self.screen)
        self.level.ship.blit(self.screen)

        for asteroid in self.level.asteroids:
            asteroid.blit(self.screen)
        for alien in self.level.aliens:
            alien.blit(self.screen)
        for item in self.level.items:
            item.blit(self.screen)
        

        