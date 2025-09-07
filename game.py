import pygame
from pygame.locals import *
import settings
from alien import Alien
from level import Level, max_level
from text import Font, Menu
from image import Image
from random import random, choice
from item import Item
from sprite import Sprite
from statusbar import Statusbar
import sound


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


        # Start the first game level
        self.level = Level(settings.game_starting_level)

        #Initializes status bar
        self.statusbar = Statusbar(self.level)

        # Starts a clock to measure ingame time
        self.clock = pygame.time.Clock()

        # Fadenkreuz
        self.aim = Sprite(Image.load('images/bullet/aim.png', scaling_width = settings.missile_explosion_size))

    def run(self):
        """Starts the main loop for the game."""
        self.running = True  # checks if the game gets shut down
        self.mode = "game"  # possible modes: "game", "menu"
        self.level.start()
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
        self.level.ship.control(keys)

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
                        self.level.ship.shoot_bullets()
                    # Keys to test the different ship-levels, only for beta-version
                    elif event.key == K_1:
                        self.level.ship.set_rank(1)
                    elif event.key == K_2:
                        self.level.ship.set_rank(2)
                    elif event.key == K_3:
                        self.level.ship.set_rank(3)
                    elif event.key == K_LSHIFT:
                        self.level.ship.activate_shield()
                if event.type == KEYUP and event.key == K_LSHIFT:
                    self.level.ship.deactivate_shield()
                if event.type == MOUSEBUTTONDOWN and event.button == 1:
                    x,y = event.pos
                    self.level.ship.shoot_missile(x,y)
            # Navigating the menu
            if self.mode == "menu":
                if event.type == KEYDOWN:
                    if event.key in [K_w, K_s]:
                        self.active_menu.move_selection(event.key)
                    if event.key == K_RETURN:
                        selection = self.active_menu.select()
                        if selection == "Restart":
                            self.mode = "game"
                            self.level.restart()
                        elif selection == "Exit":
                            self.running = False
                            break
                        elif selection == "Continue":
                            self.mode = "game"
                            if self.active_menu == self.level_solved_menu:
                                self.level.next()

    def update_sprites(self, dt):
        """update position of all sprites according to the passed time"""
        self.level.update(dt)

        self.aim.rect.center = pygame.mouse.get_pos()
        self.aim.x = self.aim.rect.x
        self.aim.y = self.aim.rect.y

    def collision_checks(self):
        """Checks for collisions of sprites, inflicts damage, adds points, generate items"""
        # Check if bullets hit aliens
        collisions = pygame.sprite.groupcollide(
            self.level.bullets, self.level.aliens, False, False, collided=pygame.sprite.collide_mask)
        for bullet in collisions.keys():
            if bullet.owner == "player":
                for alien in collisions[bullet]:
                    if bullet.type != "missile":
                        alien.get_damage(bullet.damage)
                        bullet.kill()
                    if bullet.type == "missile" and alien not in bullet.hit_enemies:
                        # missiles hit each enemy at most once during their explosion time
                        alien.get_damage(bullet.damage)
                        bullet.hit_enemies.add(alien)

        # Check if bullets hit the ship
        for bullet in self.level.bullets:
            if bullet.owner == "enemy" and pygame.sprite.collide_mask(self.level.ship, bullet):
                if self.level.ship.status == "shield":
                    bullet.reflect()
                    bullet.owner = "player"
                else:
                    self.level.ship.get_damage(bullet.damage)
                    bullet.kill()
                    sound.player_hit.play()

        # Check if aliens hit the ship
        for alien in self.level.aliens:
            if pygame.sprite.collide_mask(self.level.ship, alien):
                if self.level.ship.status == "shield":
                    alien.reflect()
                else:
                    self.level.ship.get_damage(alien.energy)
                    alien.energy = 0
                    alien.kill()
        

        # Check if ship collects an item
        for item in self.level.items:
            if pygame.sprite.collide_mask(self.level.ship, item):
                if self.level.ship.status == "shield":
                    item.change_direction(-item.direction[0],-item.direction[1])
                else:
                    self.level.ship.collect_item(item.type)
                    item.kill()

    def check_level_status(self):
        """Check if the current level is solved or the player is game over"""
        if not self.level.status() == "running":
            self.mode = "menu"
            if self.level.status() == "solved":
                self.active_menu = self.level_solved_menu
            elif self.level.status() == "game won":
                self.active_menu = self.game_won_menu
            elif self.level.status() == "game over":
                self.active_menu = self.game_over_menu

    def update_screen(self):
        """Updates screen with all sprites and stats"""
        self.screen.fill(settings.bg_color)

        # first blit the status bar onto the screen
        self.statusbar.blit(self.screen)

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
        self.level.ship.blit(self.screen)

        for alien in self.level.aliens:
            alien.blit(self.screen)
        for item in self.level.items:
            item.blit(self.screen)

        