import pygame

# sound library for convenient access from other modules

pygame.mixer.init()

#enemy sounds
alien_spawn = pygame.mixer.Sound("sounds/alien_spawn.wav")
alienblob = pygame.mixer.Sound("sounds/alienblob.wav")
blob_merge = pygame.mixer.Sound("sounds/blob_merge.ogg")
blob_spawns = pygame.mixer.Sound("sounds/blob_spawns.ogg")

#shooting sounds
alienshoot1 = pygame.mixer.Sound("sounds/alienshoot1.wav")
alienshoot2 = pygame.mixer.Sound("sounds/alienshoot2.wav")
alienshoot3 = pygame.mixer.Sound("sounds/alienshoot3.wav")
blubber = pygame.mixer.Sound("sounds/blubber.ogg")
bullet = pygame.mixer.Sound("sounds/bullet.wav")
enemy_shoot = pygame.mixer.Sound("sounds/enemy_shoot.ogg")
explosion = pygame.mixer.Sound("sounds/explosion.ogg")
shoot = pygame.mixer.Sound("sounds/shoot.ogg")

#hitting sounds
metal_hit = pygame.mixer.Sound("sounds/metal_hit.ogg")
player_hit = pygame.mixer.Sound("sounds/player_hit.ogg")
slime_hit = pygame.mixer.Sound("sounds/slime_hit.ogg")
asteroid = pygame.mixer.Sound("sounds/asteroid.ogg")
asteroid.set_volume(0.5)
small_asteroid = pygame.mixer.Sound("sounds/small_asteroid.ogg")
enemy_hit = pygame.mixer.Sound("sounds/enemy_hit.ogg")

#item sounds
bad_item = pygame.mixer.Sound("sounds/bad_item.ogg")
collect_missile = pygame.mixer.Sound("sounds/collect_missile.ogg")
extra_life = pygame.mixer.Sound("sounds/extra_life.ogg")
good_item = pygame.mixer.Sound("sounds/good_item.wav")
grow = pygame.mixer.Sound("sounds/grow.ogg")
item_collect = pygame.mixer.Sound("sounds/item_collect.ogg")
lose_life = pygame.mixer.Sound("sounds/lose_life.ogg")
ship_level_up = pygame.mixer.Sound("sounds/ship_level_up.ogg")
shrink = pygame.mixer.Sound("sounds/shrink.ogg")

#level status sounds
game_over = pygame.mixer.Sound("sounds/game_over.wav")
game_won = pygame.mixer.Sound("sounds/game_won.ogg")
level_solved = pygame.mixer.Sound("sounds/start.ogg")

#menu sounds
menu_move = pygame.mixer.Sound("sounds/menu_move.wav")
menu_select = pygame.mixer.Sound("sounds/menu_select.wav")
new_highscore = pygame.mixer.Sound("sounds/new_highscore.ogg")

#shield sounds
shield = pygame.mixer.Sound("sounds/shield.ogg")
shield_reflect = pygame.mixer.Sound("sounds/shield_reflect.ogg")

#unused sounds
teleport = pygame.mixer.Sound("sounds/teleport.wav")
laser1 = pygame.mixer.Sound("sounds/laser1.wav")
laser2 = pygame.mixer.Sound("sounds/laser2.wav")