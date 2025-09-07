import pygame
from image import Image
import settings

class Statusbar:
    '''class to format all game stats into a nice bar to blit it onto the screen'''
    def __init__(self, level, rescaling = True):
            '''First loads and positions all the images to figure out the total width,
                then (if desired) rescales all images according to the screen_width'''
            self.level = level

            self.load_images()
            self.position_stats()            

            if rescaling:
                #calculate scaling factor to fill out the entire screen width
                self.factor = settings.screen_width/self.w
                self.h = self.factor*self.h
                self.w = self.factor*self.w

                #rescaling all images according to the optimal size of the status bar
                for image in [self.empty_bar, self.health_bar, self.lives_icon, self.energy_icon, self.shield_icon, self.shield_bar, self.missiles_icon]:
                    image.surface = image.scale_by(self.factor).surface
                #recalculate all positions of the stats and font sizes
                self.position_stats(factor = self.factor) 

    def load_images(self):
            self.empty_bar = Image.load("images/statusbar/empty_bar.png")
            self.health_bar = Image.load("images/statusbar/health_bar.png")
            self.lives_icon = Image.load("images/statusbar/lives_icon.png", scaling_height = self.empty_bar.h)
            self.energy_icon = Image.load("images/statusbar/energy_icon.png", scaling_height = self.empty_bar.h)
            self.shield_icon = Image.load("images/statusbar/shield_icon.png", scaling_height = self.empty_bar.h)
            self.shield_bar = Image.load("images/statusbar/shield_bar.png")
            self.missiles_icon = Image.load("images/statusbar/missiles_icon.png", scaling_height = self.empty_bar.h)

    def position_stats(self, factor = 1):        
            #the sizes of the images determine the sizes of the fonts and all icons
            self.y = 0
            self.h = self.empty_bar.h
            self.font_size = int(7/8*self.h)
            
            self.level_number_x = 0
            self.level_number_y = self.y + 1/16*self.h

            self.lives_icon_x = self.level_number_x+21/8*self.h
            self.lives_icon_y = self.y
            self.lives_x = self.lives_icon_x + self.lives_icon.w+1/16*self.h
            self.lives_y = self.y+1/16*self.h
            self.font = pygame.font.Font(settings.stats_font, self.font_size)

            self.energy_icon_x = self.lives_x+7/4*self.h
            self.energy_icon_y = self.y
            self.bar_x = self.energy_icon_x+self.energy_icon.w
            self.bar_y = self.y
            self.health_x = self.bar_x + 19*factor
            self.health_y = self.bar_y + 18*factor
            
            self.shield_icon_x = self.bar_x+self.empty_bar.w+1/8*self.h
            self.shield_icon_y = self.y
            self.shield_bar_x = self.shield_icon_x+self.shield_icon.w
            self.shield_bar_y = self.y
            self.shield_timer_x = self.shield_bar_x + 19*factor
            self.shield_timer_y = self.shield_bar_y + 18*factor

            self.missiles_icon_x = self.shield_bar_x+self.empty_bar.w+1/8*self.h
            self.missiles_icon_y = self.y
            self.missiles_x = self.missiles_icon_x + self.missiles_icon.w+1/16*self.h
            self.missiles_y = self.y+1/16*self.h

            self.w = self.missiles_x + 7/4*self.h
            self.x = (settings.screen_width-self.w)/2

            self.score_font_size = int(self.font_size/2)
            self.score_font = pygame.font.Font(settings.stats_font, self.score_font_size)
            self.score_y = self.y + 33/32*self.h

    def blit(self, screen):
            #blits first line
            self.level_number = self.font.render(f"L{self.level.number%100:02d}", False, (255, 255, 255))
            self.lives = self.font.render(f"{self.level.ship.lives%100:02d}", False, (255, 255, 255))
            self.missiles = self.font.render(f"{self.level.ship.missiles%100:02d}", False, (255, 255, 255))
            screen.blit(self.level_number,(self.x+self.level_number_x,self.level_number_y))
            screen.blit(self.lives_icon.surface,(self.x+self.lives_icon_x,self.lives_icon_y))
            screen.blit(self.lives_icon.surface,(self.x+self.lives_icon_x,self.lives_icon_y))
            screen.blit(self.lives,(self.x+self.lives_x,self.lives_y))
            screen.blit(self.energy_icon.surface,(self.x+self.energy_icon_x,self.energy_icon_y))
            screen.blit(self.empty_bar.surface,(self.x+self.bar_x,self.bar_y))
            screen.blit(self.health_bar.surface,(self.x+self.health_x,self.health_y), area=(0,0,self.level.ship.energy/self.level.ship.max_energy*self.health_bar.w,self.health_bar.h))
            screen.blit(self.shield_icon.surface,(self.x+self.shield_icon_x,self.shield_icon_y))
            screen.blit(self.empty_bar.surface,(self.x+self.shield_bar_x,self.shield_bar_y))
            screen.blit(self.shield_bar.surface,(self.x+self.shield_timer_x,self.shield_timer_y), area=(0,0,self.level.ship.shield_timer/(1000*settings.max_shield_duration)*self.shield_bar.w,self.shield_bar.h))
            screen.blit(self.missiles_icon.surface,(self.x+self.missiles_icon_x,self.missiles_icon_y))
            screen.blit(self.missiles,(self.x+self.missiles_x,self.missiles_y))
            
            #blits second line, prints the score in green when the score buff item is activated
            #screen.blit(self.score,((settings.screen_width-self.score.get_width())/2,self.score_y))
            self.score = self.score_font.render(f"Score {int(self.level.ship.score)}", False, {False: (255,255,255), True:(100, 255, 100)}[self.level.ship.score_factor > 1])
            self.goal = self.score_font.render(self.level.goal, False, (255, 255, 255))
            self.progress = self.score_font.render(self.level.progress, False, (255, 255, 255))
            self.goal_x = max(self.score.get_width(),(settings.screen_width-self.goal.get_width())/2)
            self.progress_x = max(self.goal_x+self.goal.get_width(), settings.screen_width-self.progress.get_width())
            screen.blit(self.score,(0,self.score_y))
            screen.blit(self.goal,(self.goal_x,self.score_y))
            screen.blit(self.progress,(self.progress_x,self.score_y))
