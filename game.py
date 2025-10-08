import pygame, sound
from settings import KEY, SCREEN
from level import Level
from statusbar import Statusbar
from menu import Menu
from random import random, choice
from display import Display
from highscores import Highscores
from physics import Vector

class Game:
    """Manage the game's logic, user input, menu and rendering loop"""

    def __init__(self):
        """Initialize the game and starting stats"""

        pygame.init()

        self.screen = Display.init(SCREEN.SIZE, SCREEN.GRID)

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
                (event.type == pygame.KEYDOWN and event.key == KEY.EXIT)
            ):
                self.running = False
                break

            # Controls in game mode
            if self.mode == "game":
                if event.type == pygame.KEYDOWN:
                    # RETURN pauses the game and opens the main menu
                    if event.key == KEY.START:
                        self.mode = "menu"
                        self.active_menu = Menu.create_main_menu(self)
                        break
                    # SPACE shoots bullets
                    elif event.key == KEY.SHOOT:
                        self.level.ship.shoot_bullets()
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.level.ship.shoot_missile(Vector(event.pos[0],event.pos[1]))

            #Enter the name into the high score table
            if self.mode == "enter name":
                self.highscores.update_name(name=self.player_name, rank=self.score_rank)
                self.active_menu = Menu.create_enter_name_menu(self)
                self.active_menu.handle_input(self, event)
                continue
                    
            # Navigating the menu
            if self.mode == "menu":
                if event.type == pygame.KEYDOWN:
                    if event.key in [KEY.UP, KEY.DOWN]:
                        self.active_menu.move_selection(event.key)
                    if event.key == KEY.START:
                        Menu.choose_current_selection(self)

        # Control ship direction and shield according to keyboard input
        if self.mode == "game":
            keys = pygame.key.get_pressed()
            self.level.ship.control(keys)   

    def render(self):
        """Blit all stats, sprites, menu etc onto the display in the correct order"""
        self.screen.fill(SCREEN.BG_COLOR) # black background
        Statusbar.blit(self.level)
        self.level.blit() # statusbar, ship, enemies, items, bullets, crosshairs
        if self.mode == "menu" or self.mode == "enter name":
            self.active_menu.blit()
        Display.update(padding_color = SCREEN.PADDING_COLOR)