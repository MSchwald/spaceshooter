from game import Game
import sys



if __name__ == '__main__':
    # Make a game instance, and run the game.

    mute = True # Mute game if playing in a container without access to sound hardware

    game = Game()
    game.run(mute)

    sys.exit()