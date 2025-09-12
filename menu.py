import pygame
from pygame.locals import *
import settings
import sound
from image import Image

#Fonts and menu formatting automatically rescale with the screen width

color = {"white":(255, 255, 255), "blue": (0, 0, 200), "yellow": (255, 255, 0),
    "light_grey": (200, 200, 255), "grey": (100, 100, 100), "red": (180, 0, 0)}

class Menu():
    """Class to create menus with a given title message and a given list of options"""
    pygame.font.init()
    menu_font_size = int(settings.menu_font_size*settings.screen_width/1600)
    text_font_size = int(settings.text_font_size*settings.screen_width/1600)
    menu_font = pygame.font.Font(settings.menu_font, menu_font_size)
    text_font = pygame.font.Font(settings.text_font, text_font_size)
    boundary_size = int(settings.menu_boundary*settings.screen_width/1600)
    title_distance = int(settings.title_menu_distance*settings.screen_width/1600)
    line_distance = int(settings.line_distance*settings.screen_width/1600)

    def __init__(self, message=["Press Return to continue."], options=["Continue"], current_selection=0, centered=False):
        self.message = message
        self.options = options
        self.centered = centered
        self.current_selection = current_selection
        self.number_of_lines = len(message)+len(options)

        self.render_lines()
        self.render_menu()

    def render_lines(self):
        """Renders each line of title message and options"""
        self.lines = (
            [Menu.text_font.render(line, False, color["white"]) for line in self.message]
            +[Menu.menu_font.render(line, False, color["light_grey"], color["blue"]) for line in self.options]
        )
        self.active_lines = (
            [Menu.menu_font.render(line, False, color["yellow"], color["grey"]) for line in self.options]
        )

    def render_menu(self):
        """Renders a complete menu window out of the rendered lines"""
        # Calculates optimal size of the menu
        self.line_height = max(line.get_height()
                               for line in self.lines)
        self.line_length = max(line.get_width()
                               for line in self.lines)
        self.h = 2*Menu.boundary_size + self.number_of_lines * \
            (self.line_height+Menu.line_distance) + \
            Menu.title_distance - Menu.line_distance
        if len(self.message) > 1:
            self.h += Menu.title_distance
        self.w = 2*Menu.boundary_size + self.line_length

        # Blit all the lines onto a blue rectangle with red boundary
        self.surface = pygame.Surface((self.w, self.h))
        self.surface.fill((color["red"]))
        background = pygame.Surface((self.w-Menu.boundary_size, self.h-Menu.boundary_size))
        background.fill(color["blue"])
        self.surface.blit(background, (Menu.boundary_size//2,Menu.boundary_size//2))
        self.line_position = []
        for i in range(self.number_of_lines):
            if i in range(1,len(self.message)) and not self.centered:
                x = Menu.boundary_size
            else:
                x = (self.w-self.lines[i].get_width())//2
            y = Menu.boundary_size+i*(self.line_height+Menu.line_distance)
            if i>0:
                y+=Menu.title_distance
            if i >= len(self.message) and len(self.message) > 1:
                y+=Menu.title_distance
            self.line_position.append((x, y))
            self.surface.blit(self.lines[i], (x, y))
            
    def blit(self, screen):
        """blits the menu with the current selection highlighted"""
        self.highlighted_surface = self.surface.copy()
        j = self.current_selection
        self.highlighted_surface.blit(self.active_lines[j], (self.line_position[j+len(self.message)]))
        screen.blit(self.highlighted_surface, ((
            screen.get_width()-self.w)//2, (screen.get_height()-self.h)//2))

    def move_selection(self, event_key):
        """Navigate through the menu"""
        sound.menu_move.play()
        self.current_selection = (
            (self.current_selection + {K_w : -1, K_s : 1}[event_key]) % len(self.options)
        )

    @classmethod
    def choose_current_selection(cls, game):
        sound.menu_select.play()
        match game.active_menu.options[game.active_menu.current_selection]:
            case "Restart" | "Start game" | "New game":
                game.mode = "game"
                game.level.restart()
            case "Continue":
                game.mode = "game"
            case "Exit":
                game.running = False
            case "Next level":
                game.mode = "game"
                game.level.next()
            case "How to play" | "Back to controlls":
                game.active_menu = controll_menu
            case "Item list" | "Previous items":
                game.active_menu = items_menu1
            case "More items":
                game.active_menu = items_menu2
            case "Highscores":
                game.active_menu = Menu.make_highscores_menu(message=["Highscores", "Do you think you can beat them?"], options=["Go back", "Delete high scores"], highscores = game.highscores)
            case "Delete high scores":
                game.highscores.load_default_highscores()
                game.active_menu = Menu.make_highscores_menu(message=["Highscores", "Do you think you can beat them?"], options=["Go back", "Delete high scores"], highscores = game.highscores)
            case "Buy Premium":
                game.active_menu = premium_menu
            case "Credits":
                game.active_menu = credits_menu
            case "Check high scores":
                game.score_rank = game.highscores.highscore_rank(game.level.ship.score)
                if game.score_rank is not None:
                    pygame.mixer.stop()
                    sound.new_highscore.play()
                    game.highscores.insert_score(name=game.player_name, score=game.level.ship.score, rank=game.score_rank)
                    game.mode = "enter name"
                else:
                    game.active_menu = Menu.make_highscores_menu(message=["No new high score!", "Your score was too low,", "maybe next time!"], options=["OK"], highscores = game.highscores)
            case _:
                game.active_menu = Menu.make_main_menu(game)

    @classmethod
    def make_highscores_menu(cls, message, options, highscores, centered=True):
        highscores.render_lines()
        menu = Menu(message + ["" for i in range(settings.max_number_of_highscores+1)], options, centered=True)
        for i in range(settings.max_number_of_highscores):
            menu.lines[len(message)+i+1] = highscores.lines[i]
        menu.render_menu()
        return menu

    @classmethod
    def make_main_menu(cls, game):
        match game.player_name, game.level.status:
            case _, "running":
                m,o = ["Pause"],["Continue", "Restart"]
            case "", "game_won":
                m,o = ["Good game!", "Do you want to play again?"],["New game"]
            case _, "game_won":
                m,o = [f"Good game, {game.player_name}!", "Do you want to play again?"],["New game"]
            case "", "game_over":
                m,o = ["Game over!","You ran out of lives!", "Do you want to play again?"],["New game"]
            case _, "game_over":
                m = ["Game over!", f"{game.player_name}, do you want to play again?"]
                o = ["New game"]
            case "", "start":
                m,o=["Space invaders","Please press RETURN"],["Start game"]
            case _, "start":
                m,o=[f"Welcome back, {game.player_name}!"],["Start game"]
        options = o + ["How to play","Highscores", "Buy Premium", "Credits", "Exit"]
        return Menu(message = m, options = options)

        menu = Menu(message + ["" for i in range(settings.max_number_of_highscores+1)], options, centered=True)
        for i in range(settings.max_number_of_highscores):
            menu.lines[len(message)+i+1] = highscores.lines[i]
        menu.render_menu()
        return menu

# Menus in the game
game_over_menu = Menu(message=["Game over!","You ran out of lives!"],
                options=["Check high scores"])
game_won_menu = Menu(message=["Congratulations!", "You have finished", "all available levels!"],
                options=["Check high scores"])
premium_menu = Menu(message=["Haha", "Did you believe there", "is a premium version?"],
                options=["Go back"])
credits_menu = Menu(message=["Credits", "Programmed with pygame", "Sprites and sound effects from",
                "pixabay.com, craftpix.net,", "opengameart.net and Google Gemini", "", "And thank you for beta testing!"],
                options=["Go back"])
controll_menu = Menu(message=["Controlls", "W,A,S,D: controll the ship", "  and navigate the menu", "SPACE: shoot bullets", "LEFT SHIFT: activate shield", "Left click: drop missile", "Escape: end the game"],
                options=["Item list","Go back"])
items_menu1 = Menu(message=["Item list", "  upgrades your bullets", "  upgrades your ship", f"  gives back {settings.hp_plus} energy", f"  inverts controlls for {settings.invert_controlls_duration}s", "  attracts items to you", f"  score multiplier {settings.item_score_buff} for {settings.score_buff_duration}s"],
                options=["More items", "Back to controlls","Back to menu"])
h = items_menu1.line_height
images = [Image.load(f"images/item/{item}.png").scale_by(h/settings.item_size) for item in ["bullets_buff","ship_buff","hp_plus","invert_controlls","magnet","score_buff"]]
for i in range(6):
    items_menu1.surface.blit(images[i].surface,items_menu1.line_position[i+1])

items_menu2 = Menu(message=["Item list","    gives or takes a life", f"    increases or decreases ship size for {settings.size_change_duration}s", f"    increases or decreases ship speed {settings.speed_change_duration}s", f"    increases shield timer by {settings.shield_duration}s,", "    use it to reflect enemies and bullets.", "    gives an extra missile.", "    They are strong, use them wisely!"],
                options=["Previous items", "Back to controlls","Back to menu"])
h = items_menu1.line_height
images = [Image.load(f"images/item/{item}.png").scale_by(h/settings.item_size) for item in ["life_plus","life_minus","size_plus","size_minus","speed_buff","speed_nerf","shield","missile"]]
for i in range(3):
    x,y = items_menu2.line_position[i+1]
    items_menu2.surface.blit(images[2*i].surface,(x,y))
    items_menu2.surface.blit(images[2*i+1].surface,(x+2*h,y))
x,y = items_menu2.line_position[4]
items_menu2.surface.blit(images[6].surface,(x+h,y))
x,y = items_menu2.line_position[6]
items_menu2.surface.blit(images[7].surface,(x+h,y))