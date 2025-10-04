import sys
from game import Game
from highscores import Highscores


if __name__ == '__main__':
    # Make a game instance, and run the game.
    game = Game()
    game.run()

    sys.exit()