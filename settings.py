from pygame.locals import *
# Overall game settings

# Screen settings
screen_width = 1600 #default: 1600
screen_height = int(9/16*screen_width)
grid_width = int(screen_width/16) #default: 100
bg_color = (0, 0, 0)

# Game settings
game_starting_level = 4
starting_score = 0

# Ship settings
ship_starting_rank = 1
rank_speed = {1: 0.5, 2: 0.6, 3: 0.7}
rank_energy = {1: 15, 2: 30, 3: 45}
ship_lives = 3
ship_width = {1:100, 2:100, 3:120}
shield_starting_timer = 15
max_shield_duration = 15

# Alien settings
asteroid_pieces = 4
alien_speed = {"big_asteroid": 0.3, "small_asteroid": 0.6, "purple": 0.4, "ufo": 1, "blob": 0.5}
alien_energy = {"big_asteroid": 4, "small_asteroid": 1, "purple": 15, "ufo": 30, "blob": 32}
alien_points = {"big_asteroid": 20,"small_asteroid": 10,
                "purple": 100, "ufo": 500, "blob": 100}
alien_width = {"big_asteroid": 100, "small_asteroid": None,
                "purple": 150, "ufo": 100, "blob": 300}
alien_width["small_asteroid"]=alien_width["big_asteroid"]*asteroid_pieces**(-1/3)
alien_colorkey = {"big_asteroid": (0,0,0), "small_asteroid": (0,0,0),
                "purple": (254,254,254), "ufo": (0,0,0), "blob": (0,0,0)}

# boundaries for the movement of the sprites
# [left, top, width, height]
ship_constraints = [0, 5/9*screen_height, screen_width, 4/9*screen_height]
alien_constraints = [0, 0, screen_width, screen_height]
item_constraints = [0, 0, screen_width, screen_height]

# Bullet settings
max_bullets = 3
starting_missiles = 10
missile_explosion_size = 150
missile_duration = 0.5
missile_damage = 15
bullet_width = {1:14, 2:18, 3:22, 4:26, "missile":missile_explosion_size, "g":26, "blubber": 150}
bullet_damage = {1:1,2:2,3:3,4:4,"missile":missile_damage, "g":3, "blubber":16}
bullet_owner = {1:"player",2:"player",3:"player",4:"player","missile":"player", "g":"enemy", "blubber": "enemy"}
bullet_speed = {1:1,2:1,3:1,4:1,"missile":0, "g":0.2, "blubber":0.4}
bullet_effect_time = {1:None,2:None,3:None,4:None,"missile":1000*missile_duration, "g":None, "blubber":None}

# Item settings
item_types = ["magnet"]#["size_plus","size_minus", "score_buff", "bullets_buff", "hp_plus", "invert_controlls", "life_plus","life_minus", "magnet", "missile", "shield", "ship_buff", "speed_buff", "speed_nerf"]
item_size = 50
invert_controlls_duration = 5
size_change_duration = 10
speed_change_duration = 5
score_buff_duration = 10
shield_duration = 3
item_probability = 1#0.3
item_speed = 0.3
hp_plus = 5
speed_buff = 1.8
speed_nerf = 1/speed_buff
item_score_buff = 1.5
item_size_plus = 1.5
item_size_minus = 1/item_size_plus

# Fonts and menu formatting
stats_font = "fonts/ARCADE_I.ttf"
menu_font = "fonts/ARCADE_N.ttf"
text_font = "fonts/ARCADE_R.ttf"
menu_font_size = 30
text_font_size = 30
menu_boundary = 20
title_menu_distance = 30
line_distance = 12

# Highscores
default_highscores = [["Markus",500],["Tobi",400],["Nadine",30],["Marc",20]]
max_number_of_highscores = 5