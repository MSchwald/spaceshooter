
import pygame
from pathlib import Path

# Structured collection of all ingame parameters for comfortable adjustment

class COLOR(tuple):
    """Color names"""
    WHITE = (255, 255, 255)
    BLUE = (0, 0, 200)
    YELLOW = (255, 255, 0)
    LIGHT_GREY = (200, 200, 255)
    DARK_GREY = (50,50,50)
    GREY = (100, 100, 100)
    RED = (180, 0, 0)
    GREEN = (100, 255, 100)
    BLACK = (0,0,0)

class KEY:
    """Key names and settings"""
    EXIT = pygame.K_ESCAPE
    UP = pygame.K_w
    DOWN = pygame.K_s
    LEFT = pygame.K_a
    RIGHT = pygame.K_d
    SHOOT = pygame.K_SPACE
    SHIELD = pygame.K_LSHIFT
    START = pygame.K_RETURN
    BACK = pygame.K_BACKSPACE

class SCREEN:
    """
    Default screen settings for the game's development.
    (display.py handles rescaling subsequent sizes to user's display settings)
    """
    PADDING_COLOR = COLOR.DARK_GREY
    BG_COLOR = COLOR.BLACK
    WIDTH, HEIGHT = 1600, 900
    SIZE = (WIDTH, HEIGHT)
    GRID = (16, 9)
    GRID_WIDTH = WIDTH // GRID[0] # 1600 / 16 = 100

class GAME_MODE:
    """Possible modes of the game to respond to user's input"""
    GAME = "game" # game is running normally
    MENU = "menu" # menu is opened by player or ending a level
    ENTER_NAME = "enter name" # entering name into high score table"
    EXIT = "exit" # game exited by the player

class LEVEL_STATUS:
    """Possible status properties of the running game level to coordinate the player's progress"""
    START = "start" # starting screen (level 0) is active, game.py opens main menu
    RUNNING = "running" # a regular level is active, menus might  be active or not
    GAME_OVER = "game_over" # player ran out of lives, game.py opens game over menu
    LEVEL_SOLVED = "level_solved" # player solved a regular level and a level menu opens
    GAME_WON = "game_won" # player solved the last level in the game, high score menu gets checked

class SHIP:
    """
    Game and ship settings upon starting the game or depending on the current rank
    """
    SCORE = 0
    LIVES = 3
    GAME_LEVEL = 1
    SHIELD_STARTING_TIMER = 3
    MAX_SHIELD_DURATION = 15
    MAX_BULLETS = 3
    STARTING_MISSILES = 1
    RANK = 1
    # Default settings depending on the ship's current rank
    SPEED = {1: 0.5, 2: 0.6, 3: 0.7}
    ENERGY = {1: 15, 2: 30, 3: 45}
    WIDTH = {1: 100, 2: 100, 3:120}

class SHIP_STATUS:
    """Possible status properties of the ship implemented in ship.py"""
    NORMAL = "normal" # yellow ship without special properties
    MAGNETIC = "magnetic" # blue ship attracting items
    SHIELD = "shield" # green ship refecting enemies, bullets and items
    INVERSE_CONTROLS = "inverse_controls" # purple ship with inverted controls

class PATH:
    BASE = Path(__file__).resolve().parent.parent
    DATA = BASE / "data"
    PREPROCESSED = DATA / "preprocessed_images"
    MEDIA = BASE / "media"
    SOUNDS = MEDIA / "sounds"
    FONTS = MEDIA / "fonts"
    IMAGES = MEDIA / "images"
    ITEM = IMAGES / "item"
    ALIEN = IMAGES / "alien"
    BULLET = IMAGES / "bullet"
    SHIP = IMAGES / "ship"
    STATUSBAR = IMAGES / "statusbar"


class FONT:
    """Fonts types and sizes in the game"""
    STATS = PATH.FONTS / "ARCADE_I.ttf"
    MENU = PATH.FONTS / "ARCADE_N.ttf"
    TEXT = PATH.FONTS / "ARCADE_R.ttf"
    MENU_SIZE = 30
    TEXT_SIZE = 30

class MENU:
    """Menu settings"""
    BOUNDARY_SIZE = 20
    TITLE_DISTANCE = 30
    LINE_DISTANCE = 12

class HIGHSCORES:
    """High scores settings"""
    DEFAULT = [["Markus",1000],["Tobi",900],["Nadine",800],["Marc",600],["Katharina",400]]
    MAX_NUMBER = 5
    MAX_NAME_LENGTH = 10

class ANIMATION_TYPE:
    """Animation types of sprites implemented in sprite.py"""
    LOOP = "loop" # frames cycle periodically
    ONCE = "once" # plays once, stops at last frame
    VANISH = "vanish" # disappears after animation completes
    PINGPONG = "pingpong" # alternates back and forth
    RANDOM = "random" # frame indices are chosen randomly
    MANUAL = "manual" # no automatic frame updates, handled externally