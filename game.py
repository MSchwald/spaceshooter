import pygame, settings, sound
from settings import Key
from alien import Alien
from level import Level
from menu import Menu
from image import Image
from random import random, choice
from item import Item
from sprite import Sprite
from display import Display
from highscores import Highscores


class Game:
    """Overall class to manage the games logic and updating the screen """

    def __init__(self):
        """Initialize the game and starting stats"""

        pygame.init()

        self.display = Display()
        self.screen = self.display.get_game_surface_with_ratio(settings.SCREEN_WIDTH,settings.SCREEN_HEIGHT)

        self.player_name = "" # Gets entered when achieving a high score 
        Menu.init_settings()
        self.level = Level(0)
        self.highscores = Highscores()  
        self.clock = pygame.time.Clock()

    def run(self):
        """Starts the main loop for the game."""
        self.running = True  # Is False when the player exits the game
        self.mode = "menu"  # possible modes: "game", "menu", "enter name" (for highscores)
        self.active_menu = Menu.create_main_menu(self)
        self.level.start_current()

        #main loop of the game
        while self.running:
            # 1) handle keyboard and mouse input
            self.handle_events()

            # measure passed time and limit the frame rate to 60fps
            dt = self.clock.tick(60)
            
            # 2) run the game for dt milliseconds (pause if in menu mode)
            if self.mode == "game" or self.level.status == "start":
                self.level.update(dt) # update all ingame objects
                if self.level.status != "running" and self.level.status != "start":
                    self.active_menu = Menu.create_level_menu(self.level)
                    self.mode = "menu"

            # 3) show the new frame of the game on the screen 
            self.render()
        pygame.quit()

    def handle_events(self):
        """handle keyboard and mouse events"""
        for event in pygame.event.get():

            # The 'X' of the window and ESCAPE end the game
            if(
                event.type == pygame.QUIT or
                (event.type == pygame.KEYDOWN and event.key == Key.EXIT)
            ):
                self.running = False
                break

            # Controls in game mode
            if self.mode == "game":
                if event.type == pygame.KEYDOWN:
                    # RETURN pauses the game and opens the main menu
                    if event.key == Key.START:
                        self.mode = "menu"
                        self.active_menu = Menu.create_main_menu(self)
                        break
                    # SPACE shoots bullets
                    elif event.key == Key.SHOOT:
                        self.level.ship.shoot_bullets()
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.level.ship.shoot_missile(event.pos)

            #Enter the name into the high score table
            if self.mode == "enter name":
                self.highscores.update_name(name=self.player_name, rank=self.score_rank)
                self.active_menu = Menu.create_enter_name_menu(self)
                self.active_menu.handle_input(self, event)
                continue
                    
            # Navigating the menu
            if self.mode == "menu":
                if event.type == pygame.KEYDOWN:
                    if event.key in [Key.UP, Key.DOWN]:
                        self.active_menu.move_selection(event.key)
                    if event.key == Key.START:
                        Menu.choose_current_selection(self)

        # Control ship direction and shield according to keyboard input
        if self.mode == "game":
            keys = pygame.key.get_pressed()
            self.level.ship.control(keys)   

    def render(self):
        """Blit all stats, sprites, menu etc onto the display in the correct order"""
        self.screen.fill(settings.BG_COLOR) # black background
        self.level.blit(self.screen) # statusbar, ship, enemies, items, bullets, crosshairs
        if self.mode == "menu" or self.mode == "enter name":
            self.active_menu.blit(self.screen)
        
        self.display.update(padding_color=settings.PADDING_COLOR)