import pygame, settings, json, string
from pathlib import Path
from menu import Menu

class Highscores:
    """class to load, render, update and save highscores"""
    def __init__(self):
        """load saved high scores or use the default ones from the settings"""
        self.allowed_chars = string.ascii_letters + string.digits # characters allowed in the players' names
        try:
            with open("highscores.json", "r", encoding="utf-8") as f:
                self.score_list = json.load(f)
        except FileNotFoundError:
            self.load_default_highscores()
        self.fill_list_with_zeros()

    @property
    def players(self):
        return [x[0] for x in self.score_list]

    @property
    def scores(self):
        return [str(x[1]) for x in self.score_list]

    def load_default_highscores(self):
        self.score_list = sorted(settings.DEFAULT_HIGHSCORES, key=lambda x: x[1], reverse=True)[:settings.MAX_NUMBER_OF_HIGHSCORES]
        self.fill_list_with_zeros()
        self.save()

    def fill_list_with_zeros(self):
        while len(self.score_list) < settings.MAX_NUMBER_OF_HIGHSCORES:
            self.score_list.append(("",0))
 
    def save(self):
        with open("highscores.json", "w", encoding="utf-8") as f:
            json.dump(self.score_list, f)

    def highscore_rank(self, score):
        beaten_scores = [i for i in range(settings.MAX_NUMBER_OF_HIGHSCORES) if score > self.score_list[i][1]]
        if beaten_scores:
            return beaten_scores[0]
        return None

    def insert_score(self, name, score, rank):
        self.score_list = self.score_list[:-1]
        self.score_list.insert(rank, [name, score])

    def update_name(self, name, rank):
        self.score_list[rank][0] = name