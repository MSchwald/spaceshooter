from pygame.locals import *
# Overall game settings

# Screen settings
screen_width = 1600
screen_height = 900
grid_width = screen_width/16
bg_color = (0, 0, 0)

# Ship settings
ship_starting_level = 1
level_speed = {1: 0.5, 2: 0.6, 3: 0.7}
level_energy = {1: 15, 2: 30, 3: 45}
ship_lives = 3
ship_width = {1:grid_width, 2:grid_width, 3:1.2*grid_width}
shield_starting_timer = 3
max_shield_duration = 15

# Alien settings
type_speed = {"big_asteroid": 0.5, "small_asteroid": 1, "purple": 0.4, "ufo": 1}
type_energy = {"big_asteroid": 4, "small_asteroid": 1, "purple": 20, "ufo": 30}
type_points = {"big_asteroid": 20,
               "small_asteroid": 10, "purple": 100, "ufo": 500}
type_width = {"big_asteroid": grid_width,
               "small_asteroid": grid_width/2, "purple": 1.5*grid_width, "ufo": grid_width}
type_colorkey = {"big_asteroid": (0,0,0),
               "small_asteroid": (0,0,0), "purple": (254,254,254), "ufo": (0,0,0)}

# Game stats
game_starting_level = 3
starting_score = 0

# boundaries for the movement of the sprites
# [left, top, width, height]
ship_constraints = [0, 5/9*screen_height, screen_width, 4/9*screen_height]
alien_constraints = [0, 0, screen_width, screen_height]
item_constraints = [0, 0, screen_width, screen_height]

# Bullet settings
max_bullets = 3
starting_missiles = 10
missile_explosion_size = 1.5*grid_width
missile_duration = 0.5
missile_damage = 15
bullet_width = {1:2*7*grid_width/100, 2:2*9*grid_width/100, 3:2*11*grid_width/100, 4:2*13*grid_width/100, "missile":missile_explosion_size, "g":7/100*grid_width}
bullet_damage = {1:1,2:2,3:3,4:4,"missile":missile_damage, "g":3}
bullet_owner = {1:"player",2:"player",3:"player",4:"player","missile":"player", "g":"enemy"}
bullet_speed = {1:1,2:1,3:1,4:1,"missile":0, "g":0.2}
bullet_effect_time = {1:None,2:None,3:None,4:None,"missile":1000*missile_duration, "g":None}

# Item settings
item_types = ["size_plus","size_minus", "score_buff", "bullets_buff", "hp_plus", "invert_controlls", "life_plus","life_minus", "magnet", "missile", "shield", "ship_buff", "speed_buff", "speed_nerf"]
item_size = 0.5*grid_width
invert_controlls_duration = 5
size_change_duration = 10
speed_change_duration = 5
score_buff_duration = 10
shield_duration = 3
item_probability = 1#0.5
item_speed = 0.3
hp_plus = 5
speed_buff = 1.8
speed_nerf = 1/speed_buff
item_score_buff = 1.5
item_size_plus = 1.5
item_size_minus = 1/item_size_plus

# Display settings
healthbar_width =2*grid_width

# Fonts
stats_font = "fonts/ARCADE_I.ttf"
menu_font = "fonts/ARCADE_N.ttf"
text_font = "fonts/ARCADE_R.ttf"
menu_boundary = 20
title_menu_distance = 30
line_distance = 12