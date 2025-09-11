import pygame
from pygame.locals import *
import settings
from alien import Alien,blob_images
from level import Level, max_level
from text import *
from image import Image
from random import random, choice
from item import Item
from sprite import Sprite
from statusbar import Statusbar
import sound
from pathlib import Path
import json,string
from screen import display_size, screen, screen_rect


class Game:
    """Overall class to manage the games logic and updating the screen """

    def __init__(self):
        """Initialize the game and starting stats"""

        pygame.init()

        # Fixes the maximal screen on the display with 16:9 ratio
        self.display = pygame.display.set_mode(display_size, pygame.FULLSCREEN)
        self.screen = screen #The game's surface

        # Load high scores or use the default ones from the settings
        try:
            with open("highscores.json", "r", encoding="utf-8") as f:
                self.highscores = json.load(f)
        except FileNotFoundError:
            if settings.default_highscores:
                self.highscores = sorted(settings.default_highscores, key=lambda x: x[1], reverse=True)[:settings.max_number_of_highscores]
        self.allowed_chars = string.ascii_letters + string.digits #allowed characters in the table

        self.level = Level(0)
        self.statusbar = Statusbar(self.level)
        self.clock = pygame.time.Clock()
        self.crosshairs = Sprite(Image.load('images/bullet/aim.png', scaling_width = settings.missile_explosion_size))

    def run(self):
        """Starts the main loop for the game."""
        self.running = True  # checks if the game gets shut down
        self.mode = "menu"  # possible modes: "game", "menu", "enter name" (for highscores)
        self.active_menu = main_menu
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
        self.check_level_status()
        self.update_sprites(dt)
        self.collision_checks()
        

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
                        self.active_menu = pause_menu
                        break
                    # SPACE shoots bullets
                    elif event.key == K_SPACE:
                        self.level.ship.shoot_bullets()
                    # Keys to test the different ship-levels, only for beta-version
                    #elif event.key == K_1:
                    #    self.level.ship.set_rank(1)
                    #elif event.key == K_2:
                    #    self.level.ship.set_rank(2)
                    #elif event.key == K_3:
                    #    self.level.ship.set_rank(3)
                    elif event.key == K_LSHIFT:
                        self.level.ship.activate_shield()
                if event.type == KEYUP and event.key == K_LSHIFT:
                    self.level.ship.deactivate_shield()
                if event.type == MOUSEBUTTONDOWN and event.button == 1:
                    x,y = event.pos
                    self.level.ship.shoot_missile(x,y)

            #Enter the name into the high score table
            if self.mode == "enter name":
                self.active_menu = Menu(message=["Congratulations!", "You achieved a new high score.", "Please enter your name and press RETURN."], options=[str(score[0]) + " " + str(score[1]) for score in self.highscores], current_selection=self.highscore_place)
                if event.type == KEYDOWN:
                    if event.key == K_BACKSPACE:
                        self.highscores[self.highscore_place][0] = self.highscores[self.highscore_place][0][:-1]
                    if event.key == K_RETURN:
                        with open("highscores.json", "w", encoding="utf-8") as f:
                            json.dump(self.highscores,f)
                        self.active_menu = highscores_checked
                        self.mode = "menu"
                    elif event.unicode in self.allowed_chars and len(self.highscores[self.highscore_place][0])<10:
                        self.highscores[self.highscore_place][0] += event.unicode
            
            # Navigating the menu
            if self.mode == "menu":
                if event.type == KEYDOWN:
                    if event.key in [K_w, K_s]:
                        self.active_menu.move_selection(event.key)
                    if event.key == K_RETURN:
                        selection = self.active_menu.select()
                        if selection in ["Restart","Start game"]:
                            self.mode = "game"
                            self.level.restart()
                        elif selection == "Exit":
                            self.running = False
                            break
                        elif selection == "Continue":
                            self.mode = "game"
                            if self.active_menu == level_solved_menu:
                                self.level.next()
                        elif selection == "Highscores":
                            self.active_menu = Menu(message=["Highscores", "Do you think you can beat them?", ""]+[str(score[0]) + " " + str(score[1]) for score in self.highscores], options=["Go back"])
                        elif selection == "Go back":
                            self.active_menu = main_menu
                        elif selection == "Buy Premium":
                            self.active_menu = premium_menu
                        elif selection == "Credits":
                            self.active_menu = credits_menu
                        elif selection == "Check high scores":
                            if len(self.highscores) < settings.max_number_of_highscores or self.level.ship.score > self.highscores[-1][1]:
                                pygame.mixer.stop()
                                sound.new_highscore.play()
                                self.highscore_place = [i for i in range(len(self.highscores)) if self.highscores[i][1]<self.level.ship.score][0]
                                self.highscores.append(["", self.level.ship.score])
                                self.highscores = sorted(self.highscores, key=lambda x: x[1], reverse=True)[:settings.max_number_of_highscores]
                                self.mode = "enter name"
                            else:
                                self.active_menu = Menu(message=["No new high score!", "Your score was too low,", "maybe next time!", ""]+[str(score[0]) + " " + str(score[1]) for score in self.highscores], options=["OK"])
                        else:
                            self.active_menu = highscores_checked
                
    def update_sprites(self, dt):
        """update position of all sprites according to the passed time"""
        self.level.update(dt)

        self.crosshairs.rect.center = pygame.mouse.get_pos()
        self.crosshairs.x = self.crosshairs.rect.x
        self.crosshairs.y = self.crosshairs.rect.y



    def collision_checks(self):
        """Checks for collisions of sprites, inflicts damage, adds points, generate items"""
        # Check if bullets hit asteroids
        collisions = pygame.sprite.groupcollide(
            self.level.bullets, self.level.asteroids, False, False, collided=pygame.sprite.collide_mask)
        for bullet in collisions.keys():
            for asteroid in collisions[bullet]:
                if bullet.type != "missile":
                    asteroid.get_damage(bullet.damage)
                    bullet.kill()
                    asteroid.kill()
                if bullet.type == "missile" and asteroid not in bullet.hit_enemies:
                    # missiles hit each enemy at most once during their explosion time
                    asteroid.get_damage(bullet.damage)
                    asteroid.kill()

        #Check if bullets hit aliens or the ship
        for bullet in self.level.bullets:
            if bullet.owner == "player":
                for alien in self.level.aliens:
                    if pygame.sprite.collide_mask(bullet, alien):
                        if bullet.type != "missile":
                            alien.get_damage(bullet.damage)
                            bullet.kill()
                        if bullet.type == "missile" and alien not in bullet.hit_enemies:
                            # missiles hit each enemy at most once during their explosion time
                            if alien.type == "blob":
                                if alien.energy == 1:
                                    alien.kill()
                                else:
                                    sound.slime_hit.play()
                                    alien.energy = alien.energy//2
                                    alien.change_image(blob_images[alien.energy-1])
                            else:
                                alien.get_damage(bullet.damage)
                            bullet.hit_enemies.add(alien)
            elif bullet.owner == "enemy" and pygame.sprite.collide_mask(bullet, self.level.ship):
                if self.level.ship.status == "shield":
                    bullet.reflect()
                    bullet.owner = "player"
                else:
                    self.level.ship.get_damage(bullet.damage)
                    bullet.kill()
                    sound.player_hit.play()
            

        # Check if enemies hit the ship
        for asteroid in self.level.asteroids:
            if pygame.sprite.collide_mask(self.level.ship, asteroid):
                if self.level.ship.status == "shield":
                    asteroid.reflect()
                else:
                    self.level.ship.get_damage(asteroid.energy)
                    asteroid.energy = 0
                    asteroid.kill()
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
                self.active_menu = level_solved_menu
            elif self.level.status() == "game won":
                self.active_menu = game_won_menu
            elif self.level.status() == "game over":
                self.active_menu = game_over_menu

    def update_screen(self):
        """Updates screen with all sprites and stats"""
        self.display.fill((50,50,50)) #padding visible if screen ratio is not 16:9
        self.screen.fill(settings.bg_color)

        self.statusbar.blit(self.screen)
        self.blit_sprites() #ship, enemies, items, bullets
        self.crosshairs.blit(self.screen)

        # pause menu
        if self.mode == "menu" or self.mode == "enter name":
            self.active_menu.blit(self.screen)

        self.display.blit(self.screen,screen_rect)

        # display the new screen
        pygame.display.flip()

    def blit_sprites(self):
        """blit the updated sprites"""
        for bullet in self.level.bullets:
            bullet.blit(self.screen)
        self.level.ship.blit(self.screen)

        for asteroid in self.level.asteroids:
            asteroid.blit(self.screen)
        for alien in self.level.aliens:
            alien.blit(self.screen)
        for item in self.level.items:
            item.blit(self.screen)

        