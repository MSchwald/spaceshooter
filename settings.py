from pygame.locals import *
# Overall game settings

# Screen settings
screen_width = 1200
screen_height = 800
bg_color = (0, 0, 0)

# Ship settings
starting_score = 0
ship_starting_level = 1
level_speed = {1: 0.5, 2: 0.6, 3: 0.7}
level_energy = {1: 10, 2: 20, 3: 30}
ship_lives = 2

# Alien settings
type_speed = {"big_asteroid": 0.5, "small_asteroid": 1, 1: 0.4, 2: 1, 3: 0.6}
type_energy = {"big_asteroid": 1, "small_asteroid": 1, 1: 5, 2: 20, 3: 5}
type_points = {"big_asteroid": 20,
               "small_asteroid": 10, 1: 100, 2: 500, 3: 100}

# Game stats
game_starting_level = 1

# boundaries for the movement of the sprites
# (left, top, width, height)
ship_constraints = [0, 500, 1200, 300]
alien_constraints = [0, 0, 1200, 800]

# Bullet settings
bullet_speed = 1
max_bullets = 3

# Fonts
stats_font = "fonts/ARCADE_I.ttf"
menu_font = "fonts/ARCADE_N.ttf"
text_font = "fonts/ARCADE_R.ttf"
menu_boundary = 20
title_menu_distance = 30
line_distance = 12
