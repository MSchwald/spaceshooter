from dataclasses import dataclass
import pygame.locals

# Structured collection of all ingame parameters for comfortable adjustment
# and creation of new templates of aliens, bullets or items

# Color and key names
class COLOR(tuple):
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
    EXIT = pygame.K_ESCAPE
    UP = pygame.K_w
    DOWN = pygame.K_s
    LEFT = pygame.K_a
    RIGHT = pygame.K_d
    SHOOT = pygame.K_SPACE
    SHIELD = pygame.K_LSHIFT
    START = pygame.K_RETURN
    BACK = pygame.K_BACKSPACE

# Standard screen settings
# (display.py handles rescaling all sizes to user's display settings)
class SCREEN:
    WIDTH, HEIGHT = 1600, 900
    SIZE = (WIDTH, HEIGHT)
    GRID = (16,9)
    GRID_WIDTH = WIDTH // GRID[0] # 1600 / 16 = 100
    PADDING_COLOR = COLOR.DARK_GREY
    BG_COLOR = COLOR.BLACK

# Game and ship starting settings
class SHIP:
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

# Alien settings and templates in the game
@dataclass
class AlienTemplate:
    name: str
    speed: float
    energy: int
    points: int
    width: int
    animation_type: str | None = None
    fps: int | None = None
    colorkey: tuple = COLOR.BLACK
    pieces: int | None = None
    acc: float | None = None
    # Alien periodically does actions after given time (in ms)
    # cycle times vary randomly between given lower and upper bound (in ms)
    alarm_min: int | None = None
    alarm_max: int | None = None

class ALIEN:
    BIG_ASTEROID = AlienTemplate("big_asteroid", 0.3, 4, 20, 100, animation_type = "loop", fps = 10, pieces = 4)
    SMALL_ASTEROID = AlienTemplate("small_asteroid",0.6, 1, 10, BIG_ASTEROID.width * BIG_ASTEROID.pieces ** (-1/3), animation_type = "loop", fps = 10)
    PURPLE = AlienTemplate("purple", 0.4, 10, 100, 150, colorkey = (254, 254, 254), alarm_min = 800, alarm_max = 1500)
    UFO = AlienTemplate("ufo", 1, 20, 500, 100, alarm_min = 800, alarm_max = 1500)
    BLOB = AlienTemplate("blob", 0.5, 32, 30, 300, pieces = 2, acc = 1/160, alarm_min = 800, alarm_max = 1500)

# Bullet settings and templates in the game
@dataclass
class BulletTemplate:
    name: str
    width: int
    damage: int
    owner: str
    speed: float
    animation_type: str | None = None
    animation_time: float | None = None

class BULLET:
    BULLET1 = BulletTemplate("1", 14, 1, "player", 1)
    BULLET2 = BulletTemplate("2", 18, 2, "player", 1)
    BULLET3 = BulletTemplate("3", 22, 3, "player", 1)
    MISSILE = BulletTemplate("explosion", 150, 15, "player", 0, animation_type = "vanish", animation_time = 0.5)
    GREEN = BulletTemplate("g", 26, 3, "enemy", 0.2, animation_type = "once", animation_time = 0.5)
    BLUBBER = BulletTemplate("blubber", 150, 16, "enemy", 0.4)

# Level settings and templates in the game
@dataclass
class AlienSpawn:
    template: AlienTemplate
    amount: int = 1
    grid: tuple[int] | None = None
    speed_factor: float | None = None
    direction: tuple[int] | None = None
    energy: int | None = None
    constraints: pygame.Rect | None = None
    boundary_behaviour: str | None = None

# Item settings and templates in the game
@dataclass
class ItemTemplate:
    name: str
    size: int = 50
    speed: int = 0.3
    effect: float | None = None
    duration: int | None = None

class ITEM:
    PROBABILITY = 0.3
    #ship size *= effect
    SIZE_PLUS = ItemTemplate("size_plus", effect = 1.5, duration = 10)
    SIZE_MINUS = ItemTemplate("size_minus", effect = 1/SIZE_PLUS.effect, duration = SIZE_PLUS.duration)
    #scored points *= effect
    SCORE_BUFF = ItemTemplate("score_buff", effect = 1.5, duration = 10)
    # bullet sizes += 1
    BULLETS_BUFF = ItemTemplate("bullets_buff")
    # health += effect
    HP_PLUS = ItemTemplate("hp_plus", effect = 5)
    # invert ship controls
    INVERT_CONTROLS = ItemTemplate("invert_controls", duration = 5)
    # ship lives += or -= 1
    LIFE_PLUS = ItemTemplate("life_plus")
    LIFE_MINUS = ItemTemplate("life_minus")
    # gravitational acceleration of items to ship = effect
    MAGNET = ItemTemplate("magnet", effect = 1/200)
    # missiles += 1
    MISSILE = ItemTemplate("missile")
    # shield timer += effect seconds
    SHIELD = ItemTemplate("shield", effect = 3)
    # ship rank += 1
    SHIP_BUFF = ItemTemplate("ship_buff")
    # ship speed *= effect
    SPEED_BUFF = ItemTemplate("speed_buff", effect = 1.8, duration = 5)
    SPEED_NERF = ItemTemplate("speed_nerf", effect = 1/SPEED_BUFF.effect, duration = SPEED_BUFF.duration)
    LIST = [SIZE_PLUS, SIZE_MINUS, SCORE_BUFF, BULLETS_BUFF, HP_PLUS, INVERT_CONTROLS,
        LIFE_PLUS, LIFE_MINUS, MAGNET, MISSILE, SHIELD, SHIP_BUFF, SPEED_BUFF, SPEED_NERF]

# Fonts and menu formatting
class FONT:
    STATS = "fonts/ARCADE_I.ttf"
    MENU = "fonts/ARCADE_N.ttf"
    TEXT = "fonts/ARCADE_R.ttf"
    MENU_SIZE = 30
    TEXT_SIZE = 30

class MENU:
    BOUNDARY_SIZE = 20
    TITLE_DISTANCE = 30
    LINE_DISTANCE = 12

# Highscore settings
DEFAULT_HIGHSCORES = [["Markus",1000],["Tobi",900],["Nadine",800],["Marc",600],["Katharina",400]]
MAX_NUMBER_OF_HIGHSCORES = 5
MAX_NAME_LENGTH = 10