from dataclasses import dataclass
import pygame.locals

# Color and key names
class Color(tuple):
    WHITE = (255, 255, 255)
    BLUE = (0, 0, 200)
    YELLOW = (255, 255, 0)
    LIGHT_GREY = (200, 200, 255)
    DARK_GREY = (50,50,50)
    GREY = (100, 100, 100)
    RED = (180, 0, 0)
    GREEN = (100, 255, 100)
    BLACK = (0,0,0)

class Key:
    EXIT = pygame.K_ESCAPE
    UP = pygame.K_w
    DOWN = pygame.K_s
    LEFT = pygame.K_a
    RIGHT = pygame.K_d
    SHOOT = pygame.K_SPACE
    SHIELD = pygame.K_LSHIFT
    START = pygame.K_RETURN
    BACK = pygame.K_BACKSPACE


# All sizes refer to the following
# standard screen settings
# (screen.py handles rescaling to user's display settings)
SCREEN_WIDTH, SCREEN_HEIGHT = 1600, 900
GRID = (16,9)
GRID_WIDTH = 100 # = 1600 / 16
PADDING_COLOR = Color.DARK_GREY
BG_COLOR = Color.BLACK

# Game and ship settings
class Ship:
    SCORE = 0
    LIVES = 3
    GAME_LEVEL = 1
    SHIELD_STARTING_TIMER = 3
    MAX_SHIELD_DURATION = 15
    MAX_BULLETS = 3
    STARTING_MISSILES = 1
    RANK = 1
    SPEED = {1: 0.5, 2: 0.6, 3: 0.7}
    ENERGY = {1: 15, 2: 30, 3: 45}
    WIDTH = {1:100, 2:100, 3:120}

# Alien settings
@dataclass
class AlienType:
    name: str
    speed: float
    energy: int
    points: int
    width: int
    animation_type: str | None = None
    fps: int | None = None
    colorkey: tuple = Color.BLACK
    pieces: int | None = None
    acceleration: float | None = None

BIG_ASTEROID = AlienType("big_asteroid", 0.3, 4, 20, 100, animation_type = "loop", fps = 10, pieces = 4)
w = BIG_ASTEROID.width * BIG_ASTEROID.pieces ** (-1/3)
SMALL_ASTEROID = AlienType("small_asteroid",0.6, 1, 10, w, animation_type = "loop", fps = 10)
PURPLE = AlienType("purple", 0.4, 10, 100, 150, colorkey = (254, 254, 254))
UFO = AlienType("ufo", 1, 20, 500, 100)
BLOB = AlienType("blob", 0.5, 32, 30, 300, pieces = 2, acceleration = 1/160)


# Bullet settings
@dataclass
class BulletType:
    name: str
    width: int
    damage: int
    owner: str
    speed: float
    animation_type: str | None = None
    animation_time: float | None = None

BULLET1 = BulletType("1", 14, 1, "player", 1)
BULLET2 = BulletType("2", 18, 2, "player", 1)
BULLET3 = BulletType("3", 22, 3, "player", 1)
MISSILE = BulletType("explosion", 150, 15, "player", 0, animation_type = "vanish", animation_time = 0.5)
GREEN_BULLET = BulletType("g", 26, 3, "enemy", 0.2, animation_type = "once", animation_time = 0.5)
BLUBBER = BulletType("blubber", 150, 16, "enemy", 0.4)

# Item settings
class Item:
    SIZE = 50
    PROBABILITY = 0.3
    SPEED = 0.3
    SHIELD_DURATION = 3
    HP_PLUS = 5
    SPEED_BUFF = 1.8
    SPEED_NERF = 1/SPEED_BUFF
    SCORE_BUFF = 1.5
    SIZE_PLUS = 1.5
    SIZE_MINUS = 1/SIZE_PLUS
    MAGNET_STRENGTH = 1/30
    TYPES = ["size_plus","size_minus", "score_buff", "bullets_buff",
            "hp_plus", "invert_controls", "life_plus","life_minus",
            "magnet", "missile", "shield", "ship_buff",
            "speed_buff", "speed_nerf"]
    EFFECT_DURATION = {"size_plus":10,"size_minus":10,
            "score_buff":10, "bullets_buff":None,
            "hp_plus":None, "invert_controls":5,
            "life_plus":None,"life_minus":None,
            "magnet":None, "missile":None,
            "shield":None, "ship_buff":None,
            "speed_buff":5, "speed_nerf":5}

# Fonts and menu formatting
class Font:
    STATS = "fonts/ARCADE_I.ttf"
    MENU = "fonts/ARCADE_N.ttf"
    TEXT = "fonts/ARCADE_R.ttf"
    MENU_SIZE = 30
    TEXT_SIZE = 30

class Menu:
    BOUNDARY_SIZE = 20
    TITLE_DISTANCE = 30
    LINE_DISTANCE = 12

# Highscores
DEFAULT_HIGHSCORES = [["Markus",1000],["Tobi",900],["Nadine",800],["Marc",600],["Katharina",400]]
MAX_NUMBER_OF_HIGHSCORES = 5
MAX_NAME_LENGTH = 10