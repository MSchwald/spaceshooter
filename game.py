import pygame, sound
from settings import KEY, SCREEN
from display import Display
from level import Level
from highscores import Highscores
from menu import Menu
from physics import Vector
from statusbar import Statusbar

class Game:
    """Initiates the game's modules, starts rendering loop,
    coordinates the game's interaction with user input, opens menus"""

    def __init__(self):
        """Initialize the game's display surface and starting stats"""
        pygame.init()
        self.screen = Display.init(SCREEN.SIZE, SCREEN.GRID)
        self.player_name = "" # Gets entered when achieving a high score 
        Menu.init_settings()
        self.level = Level(0) # Level 0 = starting screen
        self.highscores = Highscores()  
        self.clock = pygame.time.Clock()

    def run(self):
        """Starts the main loop for the game."""
        self.running = True
        self.mode = "menu"  # possible modes: "game", "menu", "enter name" (for highscores)
        self.active_menu = Menu.create_main_menu(self)
        self.level.start_current()

        #main loop of the game
        while self.running:
            self.handle_user_input()

            # measure passed time dt since last frame, limit frame rate to 60fps
            dt = self.clock.tick(60)
            
            # run the game's level for dt milliseconds (pause if in menu mode)
            if self.mode == "game" or self.level.status == "start":
                self.level.update(dt) # update all ingame objects
                if self.level.status != "running" and self.level.status != "start":
                    self.active_menu = Menu.create_level_menu(self.level)
                    self.mode = "menu"
            self.render()
        pygame.quit()

    def handle_user_input(self):
        """handles keyboard and mouse events on each frame"""
        for event in pygame.event.get():

            # ESCAPE ends the game
            if(
                event.type == pygame.QUIT or
                (event.type == pygame.KEYDOWN and event.key == KEY.EXIT)
            ):
                self.running = False
                break

            # The game's reaction on pressing or releasing keys and mouse buttons
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

            # Enter the name into the high score table
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

        # Ship direction and shield are set according to the keys' current states
        if self.mode == "game":
            keys = pygame.key.get_pressed()
            self.level.ship.control(keys)   

    def render(self):
        """Blit stats, sprites (and optionally menu) onto the display in the correct order"""
        self.screen.fill(SCREEN.BG_COLOR) # background
        Statusbar.blit(self.level)
        self.level.blit() # ship, enemies, items, bullets, crosshairs
        if self.mode == "menu" or self.mode == "enter name":
            self.active_menu.blit()
        Display.update(padding_color = SCREEN.PADDING_COLOR)