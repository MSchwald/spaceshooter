import pygame
from src.settings import PATH

class MuteSound:
    """A mock class imitating pygame.mixer.Sound without doing anything."""
    def __init__(self, *args, **kwargs):
        pass
    def play(self, *args, **kwargs):
        pass
    def set_volume(self, *args, **kwargs):
        pass 
    def stop(self, *args, **kwargs):
        pass

class Sound:
    """Sound library for convenient access from other modules"""
    SOUND_PATHS = []
    @classmethod
    def init(cls, mute: bool = False):
        SoundClass = MuteSound
        if not mute:        
            try:
                pygame.mixer.init()
                SoundClass = pygame.mixer.Sound
            except pygame.error as e:
                print(f"Warning: Can't initialize pygame mixer. ({e})")
                SoundClass = MuteSound  
               
        # Enemy sounds
        cls.alien_spawn = SoundClass(PATH.SOUNDS / "alien_spawn.wav")
        cls.alienblob = SoundClass(PATH.SOUNDS / "alienblob.wav")
        cls.blob_merge = SoundClass(PATH.SOUNDS / "blob_merge.ogg")
        cls.blob_spawns = SoundClass(PATH.SOUNDS / "blob_spawns.ogg")

        # Shooting sounds
        cls.alienshoot1 = SoundClass(PATH.SOUNDS / "alienshoot1.wav")
        cls.alienshoot2 = SoundClass(PATH.SOUNDS / "alienshoot2.wav")
        cls.alienshoot3 = SoundClass(PATH.SOUNDS / "alienshoot3.wav")
        cls.blubber = SoundClass(PATH.SOUNDS / "blubber.ogg")
        cls.bullet = SoundClass(PATH.SOUNDS / "bullet.wav")
        cls.enemy_shoot = SoundClass(PATH.SOUNDS / "enemy_shoot.ogg")
        cls.explosion = SoundClass(PATH.SOUNDS / "explosion.ogg")
        cls.shoot = SoundClass(PATH.SOUNDS / "shoot.ogg")

        # Hitting sounds
        cls.metal_hit = SoundClass(PATH.SOUNDS / "metal_hit.ogg")
        cls.player_hit = SoundClass(PATH.SOUNDS / "player_hit.ogg")
        cls.slime_hit = SoundClass(PATH.SOUNDS / "slime_hit.ogg")
        cls.asteroid = SoundClass(PATH.SOUNDS / "asteroid.ogg")
        cls.asteroid.set_volume(0.5)
        cls.small_asteroid = SoundClass(PATH.SOUNDS / "small_asteroid.ogg")
        cls.enemy_hit = SoundClass(PATH.SOUNDS / "enemy_hit.ogg")

        # Item sounds
        cls.bad_item = SoundClass(PATH.SOUNDS / "bad_item.ogg")
        cls.collect_missile = SoundClass(PATH.SOUNDS / "collect_missile.ogg")
        cls.extra_life = SoundClass(PATH.SOUNDS / "extra_life.ogg")
        cls.good_item = SoundClass(PATH.SOUNDS / "good_item.wav")
        cls.grow = SoundClass(PATH.SOUNDS / "grow.ogg")
        cls.item_collect = SoundClass(PATH.SOUNDS / "item_collect.ogg")
        cls.lose_life = SoundClass(PATH.SOUNDS / "lose_life.ogg")
        cls.ship_level_up = SoundClass(PATH.SOUNDS / "ship_level_up.ogg")
        cls.shrink = SoundClass(PATH.SOUNDS / "shrink.ogg")

        # Level status sounds
        cls.game_over = SoundClass(PATH.SOUNDS / "game_over.wav")
        cls.game_won = SoundClass(PATH.SOUNDS / "game_won.ogg")
        cls.level_solved = SoundClass(PATH.SOUNDS / "start.ogg")

        # Menu sounds
        cls.menu_move = SoundClass(PATH.SOUNDS / "menu_move.wav")
        cls.menu_select = SoundClass(PATH.SOUNDS / "menu_select.wav")
        cls.new_highscore = SoundClass(PATH.SOUNDS / "new_highscore.ogg")

        # Shield sounds
        cls.shield = SoundClass(PATH.SOUNDS / "shield.ogg")
        cls.shield_reflect = SoundClass(PATH.SOUNDS / "shield_reflect.ogg")

        # Unused sounds
        cls.teleport = SoundClass(PATH.SOUNDS / "teleport.wav")
        cls.laser1 = SoundClass(PATH.SOUNDS / "laser1.wav")
        cls.laser2 = SoundClass(PATH.SOUNDS / "laser2.wav")