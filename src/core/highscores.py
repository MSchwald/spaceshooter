import json
from src.settings import HIGHSCORES, PATH
from string import ascii_letters, digits

class Highscores:
    """Load, render, update and save highscores"""

    def __init__(self):
        """load saved high scores or the default ones from the settings"""
        self.allowed_chars = ascii_letters + digits # characters allowed in the players' names
        try:
            with open(PATH.DATA / "highscores.json", "r", encoding="utf-8") as f:
                self.score_list = json.load(f)
        except FileNotFoundError:
            self.load_default_highscores()
        self.fill_list_with_zeros()

    @property
    def players(self) -> list[str]:
        return [x[0] for x in self.score_list]

    @property
    def scores(self) -> list[str]:
        return [str(x[1]) for x in self.score_list]

    def load_default_highscores(self):
        self.score_list = sorted(HIGHSCORES.DEFAULT, key=lambda x: x[1], reverse=True)[:HIGHSCORES.MAX_NUMBER]
        self.fill_list_with_zeros()
        self.save()

    def fill_list_with_zeros(self):
        """When the default high score list in the settings is to short, fill the table with zeros."""
        while len(self.score_list) < HIGHSCORES.MAX_NUMBER:
            self.score_list.append(("",0))
 
    def save(self):
        with open(PATH.DATA / "highscores.json", "w", encoding="utf-8") as f:
            json.dump(self.score_list, f)

    def highscore_rank(self, score: int) -> int | None:
        """For a given score, return its rank in the high score table. Return None if the score is too low."""
        beaten_scores = [i for i in range(HIGHSCORES.MAX_NUMBER) if score > self.score_list[i][1]]
        if beaten_scores:
            return beaten_scores[0]
        return None

    def insert_score(self, name: str, score: int, rank: int):
        self.score_list = self.score_list[:-1]
        self.score_list.insert(rank, [name, score])

    def update_name(self, name: str, rank: int):
        self.score_list[rank][0] = name