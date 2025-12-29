from dataclasses import dataclass
from src.settings import COLOR, ANIMATION_TYPE

#Templates for creating sprites: aliens, bullets, items

@dataclass
class SpriteTemplate:
    name: str
    speed: float
    width: int
    animation_type: str | None = None
    fps: int | None = None
    colorkey: tuple = COLOR.BLACK
    acc: float | None = None
    
@dataclass
class AlienTemplate:
    """Capture the defining properties of an enemy species"""
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
    """Default settings of enemiy species in the game"""
    BIG_ASTEROID = AlienTemplate("big_asteroid", 0.3, 4, 20, 100, animation_type = ANIMATION_TYPE.LOOP, fps = 10, pieces = 4)
    SMALL_ASTEROID = AlienTemplate("small_asteroid",0.6, 1, 10, BIG_ASTEROID.width * BIG_ASTEROID.pieces ** (-1/3), animation_type = ANIMATION_TYPE.LOOP, fps = 10)
    PURPLE = AlienTemplate("purple", 0.4, 10, 100, 150, colorkey = (254, 254, 254), alarm_min = 800, alarm_max = 1500)
    UFO = AlienTemplate("ufo", 1, 20, 500, 100, alarm_min = 800, alarm_max = 1500)
    BLOB = AlienTemplate("blob", 0.5, 32, 30, 300, animation_type = ANIMATION_TYPE.MANUAL, pieces = 2, acc = 1/160, alarm_min = 800, alarm_max = 1500)

# Bullet settings and templates in the game
@dataclass
class BulletTemplate:
    """Capture the defining properties of a bullet type"""
    name: str
    width: int
    damage: int
    owner: str
    speed: float
    animation_type: str | None = None
    animation_time: float | None = None

class BULLET:
    """Default settings of bullet types in the game"""
    BULLET1 = BulletTemplate("1", 14, 1, "player", 1)
    BULLET2 = BulletTemplate("2", 18, 2, "player", 1)
    BULLET3 = BulletTemplate("3", 22, 3, "player", 1)
    MISSILE = BulletTemplate("explosion", 150, 15, "player", 0, animation_type = ANIMATION_TYPE.VANISH, animation_time = 0.5)
    GREEN = BulletTemplate("g", 26, 3, "enemy", 0.2, animation_type = ANIMATION_TYPE.ONCE, animation_time = 0.5)
    BLUBBER = BulletTemplate("blubber", 150, 16, "enemy", 0.4)

@dataclass
class ItemTemplate:
    """Capture the defining properties of an item type"""
    name: str
    size: int = 50
    speed: int = 0.3
    effect: float | None = None
    duration: int | None = None

class ITEM:
    """Default settings of item types in the game"""
    # Probability of an item spawn for each defeated enemy
    PROBABILITY = 0.3
    # ship size *= effect
    SIZE_PLUS = ItemTemplate("size_plus", effect = 1.5, duration = 10)
    SIZE_MINUS = ItemTemplate("size_minus", effect = 1/SIZE_PLUS.effect, duration = SIZE_PLUS.duration)
    # scored points *= effect
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

