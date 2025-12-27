from game import Game
import sys



if __name__ == '__main__':
    # Make a game instance, and run the game.

    mute = False # Mute game if playing in a container without access to sound hardware

    if "mute" in sys.argv:
        mute = True
    
    game = Game()
    game.run(mute)

    sys.exit()