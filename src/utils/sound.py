import pygame

class MuteSound:
    """A mock class imitating pygame.mixer.Sound without doing anything."""
    def __init__(self, *args, **kwargs):
        pass # Ignoriere alle Initialisierungsargumente
    def play(self, *args, **kwargs):
        pass
    def set_volume(self, *args, **kwargs): # set_volume muss auch gemockt werden!
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
        cls.alien_spawn = SoundClass("sounds/alien_spawn.wav")
        cls.alienblob = SoundClass("sounds/alienblob.wav")
        cls.blob_merge = SoundClass("sounds/blob_merge.ogg")
        cls.blob_spawns = SoundClass("sounds/blob_spawns.ogg")

        # Shooting sounds
        cls.alienshoot1 = SoundClass("sounds/alienshoot1.wav")
        cls.alienshoot2 = SoundClass("sounds/alienshoot2.wav")
        cls.alienshoot3 = SoundClass("sounds/alienshoot3.wav")
        cls.blubber = SoundClass("sounds/blubber.ogg")
        cls.bullet = SoundClass("sounds/bullet.wav")
        cls.enemy_shoot = SoundClass("sounds/enemy_shoot.ogg")
        cls.explosion = SoundClass("sounds/explosion.ogg")
        cls.shoot = SoundClass("sounds/shoot.ogg")

        # Hitting sounds
        cls.metal_hit = SoundClass("sounds/metal_hit.ogg")
        cls.player_hit = SoundClass("sounds/player_hit.ogg")
        cls.slime_hit = SoundClass("sounds/slime_hit.ogg")
        cls.asteroid = SoundClass("sounds/asteroid.ogg")
        cls.asteroid.set_volume(0.5)
        cls.small_asteroid = SoundClass("sounds/small_asteroid.ogg")
        cls.enemy_hit = SoundClass("sounds/enemy_hit.ogg")

        # Item sounds
        cls.bad_item = SoundClass("sounds/bad_item.ogg")
        cls.collect_missile = SoundClass("sounds/collect_missile.ogg")
        cls.extra_life = SoundClass("sounds/extra_life.ogg")
        cls.good_item = SoundClass("sounds/good_item.wav")
        cls.grow = SoundClass("sounds/grow.ogg")
        cls.item_collect = SoundClass("sounds/item_collect.ogg")
        cls.lose_life = SoundClass("sounds/lose_life.ogg")
        cls.ship_level_up = SoundClass("sounds/ship_level_up.ogg")
        cls.shrink = SoundClass("sounds/shrink.ogg")

        # Level status sounds
        cls.game_over = SoundClass("sounds/game_over.wav")
        cls.game_won = SoundClass("sounds/game_won.ogg")
        cls.level_solved = SoundClass("sounds/start.ogg")

        # Menu sounds
        cls.menu_move = SoundClass("sounds/menu_move.wav")
        cls.menu_select = SoundClass("sounds/menu_select.wav")
        cls.new_highscore = SoundClass("sounds/new_highscore.ogg")

        # Shield sounds
        cls.shield = SoundClass("sounds/shield.ogg")
        cls.shield_reflect = SoundClass("sounds/shield_reflect.ogg")

        # Unused sounds
        cls.teleport = SoundClass("sounds/teleport.wav")
        cls.laser1 = SoundClass("sounds/laser1.wav")
        cls.laser2 = SoundClass("sounds/laser2.wav")
    
    