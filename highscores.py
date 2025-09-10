from pathlib import Path
import json
import settings
import string
from text import Menu

#unused, might be used later to refactor game.py

class Highscores:
    player_name = None
    highscores = []

    @classmethod
    def check(cls,active_menu,score):
        try:
            with open("highscores.json", "r", encoding="utf-8") as f:
                cls.highscores = json.load(f)
        except FileNotFoundError:
            if settings.default_highscores:
                cls.highscores = settings.default_highscores
        if len(cls.highscores) < settings.max_number_of_highscores or score > cls.highscores[-1][1]:
            allowed_chars = string.ascii_letters + string.digits
            name = ""
            enter_pressed = False
            while not enter_pressed:
                active_menu = Menu(message=["Congratulations!", "You achieved a new high score.", "Please enter your name and press RETURN."], options=["Name:"])
                for event in pygame.event.get():
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_RETURN:
                            enter_pressed = True
                        elif event.key == pygame.K_BACKSPACE:
                            name = name[:-1]
                        elif event.unicode in allowed_chars and len(name)<=10:
                            name += event.unicode
            Highscores.update(score)
        else:
            active_menu = Menu(message=["No new high score!", "Your score was too low, maybe next time!"], options=["OK"])

    
    @classmethod
    def enter_player_name():
        allowed_chars = string.ascii_letters + string.digits
        name = ""
        enter_pressed = False
        while not enter_pressed:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        enter_pressed = True
                    elif event.key == pygame.K_BACKSPACE:
                        name = name[:-1]
                    elif event.unicode in allowed_chars and len(name)<=10:
                        name += event.unicode

    @classmethod
    def update(cls, player_name, score):
        if player_name is None:
            player_name = "anonymous"
        try:
            with open("highscores.json", "r", encoding="utf-8") as f:
                highscores = json.load(f)
        except FileNotFoundError:
            if settings.default_highscores:
                highscores = settings.default_highscores
            else:
                highscores = []
        if len(highscores) < settings.max_number_of_highscores or score > highscores[-1][1]:
            cls.new_highscore = True
            highscores.append([player_name,score])
            #keep the top scores in a sorted format
            highscores = sorted(highscores, key=lambda x: x[1], reverse=True)[:settings.max_number_of_highscores]
            with open("highscores.json", "w", encoding="utf-8") as f:
                highscores = json.dump(highscores,f)
        else:
            cls.new_highscore = False
