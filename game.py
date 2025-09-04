import pygame
from pygame.locals import *
import settings
from ship import Ship
from alien import Alien
from level import Level, max_level
from text import Font, Menu
from math import pi
from image import Image
from random import random, choice
from item import Item
from sprite import Sprite
from statusbar import Statusbar


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

        #Initializes status bar
        self.statusbar = Statusbar()

        # Start the first game level
        self.level = Level(settings.game_starting_level)

        # Starts a clock to measure ingame time
        self.clock = pygame.time.Clock()

        # Fadenkreuz
        self.aim = Sprite(Image.load('images/bullet/aim.png', scaling_width = settings.missile_explosion_size))

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
        self.check_level_status()

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
                    elif event.key == K_SPACE:
                        self.ship.shoot_bullets(self.level)
                    # Keys to test the different ship-levels, only for beta-version
                    elif event.key == K_1:
                        self.ship.set_level(1)
                    elif event.key == K_2:
                        self.ship.set_level(2)
                    elif event.key == K_3:
                        self.ship.set_level(3)
                    elif event.key == K_LSHIFT:
                        self.ship.activate_shield()
                if event.type == KEYUP and event.key == K_LSHIFT:
                    self.ship.deactivate_shield()
                if event.type == MOUSEBUTTONDOWN and event.button == 1:
                    x,y = event.pos
                    self.ship.shoot_missile(self.level,x,y)
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
        for bullet in self.level.bullets:
            bullet.update(dt)

        self.ship.update(dt)

        for alien in self.level.aliens:
            alien.update(dt)
        for item in self.level.items:
            item.update(dt, self.ship)

        self.aim.rect.center = pygame.mouse.get_pos()
        self.aim.x = self.aim.rect.x
        self.aim.y = self.aim.rect.y

    def collision_checks(self):
        """Checks for collisions of sprites, inflicts damage, adds points, generate items"""
        # Check if bullets hit aliens
        collisions = pygame.sprite.groupcollide(
            self.level.bullets, self.level.aliens, False, False, collided=pygame.sprite.collide_mask)
        for bullet in collisions.keys():
            for alien in collisions[bullet]:
                if bullet.type != "missile":
                    bullet.kill()
                if bullet.type != "missile" or alien not in bullet.hit_enemies:
                    alien.get_damage(bullet.damage)
                    if bullet.type == "missile":
                        bullet.hit_enemies.add(alien)
                    if alien.energy <= 0 or alien.type == "big_asteroid":
                        if alien.type == "big_asteroid":
                            pieces = [
                                Alien("small_asteroid", center=alien.rect.center, direction=alien.direction) for i in range(4)]
                            for i in range(4):
                                pieces[i].turn_direction((2*i+1)*pi/4)
                                self.level.aliens.add(pieces[i])
                        self.ship.score += self.ship.score_factor*alien.points
                        if random() <= settings.item_probability:
                            self.level.items.add(Item(choice(settings.item_types),center=alien.rect.center))
                        alien.remove(self.level.aliens)

        # Check if aliens hit the ship
        for alien in self.level.aliens:
            if pygame.sprite.collide_mask(self.ship, alien):
                if self.ship.status == "shield":
                    alien.change_direction(-alien.direction[0],-alien.direction[1])
                else:
                    self.ship.get_damage(alien.energy)
                    self.ship.score += self.ship.score_factor*alien.points
                    alien.kill()

        # Check if ship collects an item
        for item in self.level.items:
            if pygame.sprite.collide_mask(self.ship, item):
                if self.ship.status == "shield":
                    item.change_direction(-item.direction[0],-item.direction[1])
                else:
                    self.ship.collect_item(item.type)
                    item.kill()

    def check_level_status(self):
        """Check if the current level is solved or the player is game over"""
        if not self.level.status(self.ship) == "running":
            self.mode = "menu"
            if self.level.status(self.ship) == "solved":
                self.active_menu = self.level_solved_menu
            elif self.level.status(self.ship) == "game won":
                self.active_menu = self.game_won_menu
            elif self.level.status(self.ship) == "game over":
                self.active_menu = self.game_over_menu

    def update_screen(self):
        """Updates screen with all sprites and stats"""
        self.screen.fill(settings.bg_color)

        # first blit the status bar onto the screen
        self.statusbar.blit(self.screen, self.ship, self.level.number)

        # then blit the updated sprites (ship, enemies, items, bullets)
        self.blit_sprites()

        # blit the aim for the missiles on top
        self.aim.blit(self.screen)

        # pause menu
        if self.mode == "menu":
            self.active_menu.blit(self.screen)

        # display the new screen
        pygame.display.flip()

    def blit_sprites(self):
        """blit the updated sprites"""
        for bullet in self.level.bullets:
            bullet.blit(self.screen)
        self.ship.blit(self.screen)

        for alien in self.level.aliens:
            alien.blit(self.screen)
        for item in self.level.items:
            item.blit(self.screen)

        