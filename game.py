import pygame
from pygame.locals import *
import settings
from ship import Ship
from alien import Alien
from level import Level, max_level
from text import Font, Menu
from math import pi
import image


class Game:
    """Overall class to manage the game stats and behavior."""

    def __init__(self):
        """Initialize the game and starting stats"""

        # Initializes all pygame modules
        pygame.init()

        # Fixes screen as a pygame surface on which we can blit sprites
        self.screen = pygame.display.set_mode(
            (settings.screen_width, settings.screen_height))

        # Initialize fonts
        self.font = Font()

        # Initialize test menu
        self.active_menu = None
        self.pause_menu = Menu(self.font, message=["PAUSE"], options=[
                               "Continue", "Restart", "Exit"])
        self.level_solved_menu = Menu(self.font, message=[
                                      "Level solved. Press RETURN", "to start the next level."], options=["Continue"])
        self.game_won_menu = Menu(self.font, message=[
                                  "Congratulations, you have", "finished all levels!"], options=["Restart", "Exit"])
        self.game_over_menu = Menu(self.font, message=[
                                  "Game over!", "you ran out of lives!"], options=["Restart", "Exit"])

        # Initializes the Ship
        self.ship = Ship()

        # Start the first game level
        self.level = Level(settings.game_starting_level)

        # Starts a clock to measure ingame time
        self.clock = pygame.time.Clock()

        # self.font = pygame.font.Font(None,50)

    def run(self):
        """Starts the main loop for the game."""
        self.running = True  # checks if the game gets shut down
        self.mode = "game"  # possible modes: "game", "menu"
        self.level.start(self.ship)
        while self.running:
            self.handle_events()

            # measures passed time and limits the frame rate to 60fps
            dt = self.clock.tick(60)
            if self.mode == "game":

                self.update(dt)

            self.render()
        pygame.quit()

    def handle_events(self):
        self.handle_event_queue()
        # set the direction of the ship according to keyboard input
        keys = pygame.key.get_pressed()
        self.ship.control(keys)

    def update(self, dt):
        self.update_sprites(dt)
        self.collision_checks()
        self.check_if_level_solved()

    def render(self):
        self.update_screen()

    def handle_event_queue(self):
        """handle the event queue"""
        for event in pygame.event.get():

            # Clicking the 'X' of the window ends the game
            if event.type == pygame.QUIT:
                self.running = False
                break
            # ESC ends the game
            if event.type == KEYDOWN and event.key == K_ESCAPE:
                self.running = False
                break
            # Controls in game mode
            if self.mode == "game":
                if event.type == KEYDOWN:
                    # RETURN pauses the game and opens the main menu
                    if event.key == K_RETURN:
                        self.mode = "menu"
                        self.active_menu = self.pause_menu
                        break
                    # SPACE shoots bullets
                    elif event.key == K_SPACE and len(self.ship.bullets) < settings.max_bullets*(2*self.ship.level-1):
                        self.ship.shoot_bullets()
                    # Keys to test the different ship-levels
                    elif event.key == K_1:
                        self.ship.set_level(1)
                    elif event.key == K_2:
                        self.ship.set_level(2)
                    elif event.key == K_3:
                        self.ship.set_level(3)
            # Navigating the menu
            if self.mode == "menu":
                if event.type == KEYDOWN:
                    if event.key in [K_w, K_s]:
                        self.active_menu.move_selection(event.key)
                    if event.key == K_RETURN:
                        selection = self.active_menu.select()
                        if selection == "Restart":
                            self.mode = "game"
                            self.level.restart(self.ship)
                        elif selection == "Exit":
                            self.running = False
                            break
                        elif selection == "Continue":
                            self.mode = "game"
                            if self.active_menu == self.level_solved_menu:
                                self.level.next(self.ship)

    def update_sprites(self, dt):
        """update position of all sprites according to the passed time"""
        for bullet in self.ship.bullets:
            bullet.update(dt)

        self.ship.update(dt)

        for alien in self.level.aliens:
            alien.update(dt)

    def collision_checks(self):
        """Checks for collisions of sprites, inflicts damage and adds points"""
        # Check if bullets hit aliens
        collisions = pygame.sprite.groupcollide(
            self.ship.bullets, self.level.aliens, True, False)
        for bullet in collisions.keys():
            for alien in collisions[bullet]:
                alien.get_damage(bullet.damage)
                if alien.energy <= 0 or alien.type == "big_asteroid":
                    if alien.type == "big_asteroid":
                        pieces = [
                            Alien(alien.x+(image.alien["big_asteroid"].w-image.alien["small_asteroid"].w)/2, alien.y+(image.alien["big_asteroid"].h-image.alien["small_asteroid"].h)/2, "small_asteroid", alien.direction) for i in range(4)]
                        for i in range(4):
                            pieces[i].turn_direction((2*i+1)*pi/4)
                            self.level.aliens.add(pieces[i])
                    alien.remove(self.level.aliens)
                    self.ship.score += alien.points

        # Check if aliens hit the ship
        collisions = pygame.sprite.spritecollide(
            self.ship, self.level.aliens, True)
        for alien in collisions:
            self.ship.get_damage(alien.energy)
            if self.ship.lives <= 0:
                self.mode = "menu"
                self.active_menu = self.game_over_menu
            self.ship.score += alien.points

    def check_if_level_solved(self):
        """Check if the current level is solved"""
        if not self.level.aliens:
            if self.level.number < max_level:
                self.mode = "menu"
                self.active_menu = self.level_solved_menu
            else:
                self.mode = "menu"
                self.active_menu = self.game_won_menu

    def update_screen(self):
        """Updates screen with all sprites and stats"""
        self.screen.fill(settings.bg_color)
        # blit the game stats onto the screen
        game_stats = self.font.stats.render(
            f"Score: {self.ship.score}, Level: {self.level.number}, Lives: {self.ship.lives}, Energy: {self.ship.energy}", False, (255, 255, 255))
        self.screen.blit(game_stats, (10, 10))

        # blit updated sprites
        self.blit_sprites()

        # pause menu
        if self.mode == "menu":
            self.active_menu.blit(self.screen)

        # display the new screen
        pygame.display.flip()

    def blit_sprites(self):
        """blit updated sprites onto the background"""
        for bullet in self.ship.bullets:
            bullet.blit(self.screen)
        self.ship.blit(self.screen)

        for alien in self.level.aliens:
            alien.blit(self.screen)
