from __future__ import annotations
import pygame, sound
from image import Image
from level import Level
from settings import COLOR, KEY, SCREEN, FONT, MENU, ITEM, MAX_NAME_LENGTH
from text import *
from display import Display

class Menu():
    """Manage creation and navigation of menus consisting of a title message and a list of options"""
    
    @classmethod
    def init_settings(cls):
        '''Rescale menu formating to user's display setting'''
        pygame.font.init()
        cls.menu_font_size = int(FONT.MENU_SIZE*Display.screen_width/SCREEN.WIDTH)
        cls.text_font_size = int(FONT.TEXT_SIZE*Display.screen_width/SCREEN.WIDTH)
        cls.menu_font = pygame.font.Font(FONT.MENU, cls.menu_font_size)
        cls.text_font = pygame.font.Font(FONT.TEXT, cls.text_font_size)
        cls.boundary_size = int(MENU.BOUNDARY_SIZE*Display.screen_width/SCREEN.WIDTH)
        cls.title_distance = int(MENU.TITLE_DISTANCE*Display.screen_width/SCREEN.WIDTH)
        cls.line_distance = int(MENU.LINE_DISTANCE*Display.screen_width/SCREEN.WIDTH)

    def __init__(self, header_surface: pygame.Surface, options: list[str], current_selection: int = 0):
        self.header_surface = header_surface
        self.inactive_options = Text(options, Menu.menu_font, COLOR.LIGHT_GREY, COLOR.BLUE)
        self.highlighted_options = Text(options, Menu.menu_font, COLOR.YELLOW, COLOR.GREY)
        self.options = Text(options, Menu.menu_font, COLOR.LIGHT_GREY, COLOR.BLUE)
        self.current_selection = current_selection
        self.highlight()
        self.rendered_menu = self.render()
        self.w = self.rendered_menu.get_width()
        self.h = self.rendered_menu.get_height()

    def highlight(self):
        self.options.rendered_lines = self.inactive_options.rendered_lines[:]
        self.options.rendered_lines[self.current_selection] = self.highlighted_options.rendered_lines[self.current_selection]

    def render(self) -> pygame.Surface:
        """Renders the the menu"""
        rendered_options = self.options.render("center",Menu.line_distance, padding_color=COLOR.BLUE, center_title=False)
        rendered_menu = align_surfaces([self.header_surface,rendered_options], orientation="vertical", spacing = Menu.title_distance, padding_size = Menu.boundary_size//2, padding_color = COLOR.BLUE)
        return pad_surface(rendered_menu, padding_size=Menu.boundary_size//2, padding_color=COLOR.RED)

    def blit(self, screen: pygame.Surface | None = None):
        """blits the menu with the current selection highlighted"""
        screen = screen or Display.screen
        screen.blit(self.rendered_menu, ((
            screen.get_width()-self.w)//2, (screen.get_height()-self.h)//2))

    def move_selection(self, event_key):
        """Navigate through the menu"""
        sound.menu_move.play()
        self.current_selection = (
            (self.current_selection + {KEY.UP : -1, KEY.DOWN : 1}[event_key]) % len(self.options.lines)
        )
        self.highlight()
        self.rendered_menu = self.render()

    @classmethod
    def create(cls, message: list[str], options: list[str],
                    current_selection: int = 0, highscores: Highscores | None = None) -> Menu:
        """Creates a menu with given title message and options,
        allows for showing the highsores in between"""
        if highscores is not None:
            message += [""]
        text = Text(message, Menu.text_font, COLOR.WHITE, COLOR.BLUE)
        rendered_message = text.render("left", Menu.line_distance, padding_color=COLOR.BLUE, title_distance=Menu.title_distance)
        if highscores is not None:
            players = Text(highscores.players, Menu.menu_font, COLOR.WHITE, COLOR.BLUE)
            scores = Text(highscores.scores, Menu.menu_font, COLOR.WHITE, COLOR.BLUE)
            rendered_players = players.render("left", Menu.line_distance, padding_color=COLOR.BLUE, center_title=False)
            rendered_scores = scores.render("right", Menu.line_distance, padding_color=COLOR.BLUE, center_title=False)
            table = align_surfaces([rendered_players,rendered_scores],orientation="horizontal",spacing=Menu.title_distance,padding_color=COLOR.BLUE)
            header_surface = align_surfaces([rendered_message,table],orientation="vertical",spacing=Menu.line_distance,padding_color=COLOR.BLUE)
        else:
            header_surface = rendered_message
        return Menu(header_surface, options, current_selection=current_selection)

    @classmethod
    def create_main_menu(cls, game: Game) -> Menu:
        """Creates the correct Main / Pause menu in each game situation"""
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
                m,o=["Space invaders", "Navigate menu with W,S","and pressing RETURN."],["Start game"]
            case _, "start":
                m,o=[f"Welcome back, {game.player_name}!"],["Start game"]
        options = o + ["How to play","Highscores", "Buy Premium", "Credits", "Exit"]
        return Menu.create(m, options)

    @classmethod
    def create_level_menu(cls, level: Level) -> Menu:
        """Returns a menu according to the given level status"""
        if level.status in ["level_solved", "game_won", "game_over"]:
            level.play_status_sound()
            match level.status:
                case "level_solved":
                    return Menu.create([f"Level {level.number} solved!",
                                f"In level {level.number+1}, you have to", f"{level.goals[level.number+1]}"],
                                ["Next level"])
                case "game_won":
                    return Menu.create(["Congratulations!", "You have finished", "all available levels!"],
                                ["Check high scores"])
                case "game_over": 
                    return Menu.create(["Game over!","You ran out of lives!"],
                                ["Check high scores"])

    @classmethod
    def create_enter_name_menu(cls, game: Game) -> Menu:
        return Menu.create(["Congratulations!", f"Your score ranks on place {game.score_rank+1}.",
                            "Please enter your name and press RETURN."],
                            [f"Name: {game.player_name}"],
                            highscores = game.highscores)

    def handle_input(self, game: Game, event):
        if event.type == pygame.KEYDOWN:
            if event.unicode in game.highscores.allowed_chars and len(game.player_name) < MAX_NAME_LENGTH:
                game.player_name += event.unicode
            elif event.key == KEY.BACK:
                game.player_name = game.player_name[:-1]
            elif event.key == KEY.START:
                    game.highscores.save()
                    game.active_menu = Menu.create_main_menu(game)
                    game.mode = "menu"

    @classmethod
    def choose_current_selection(cls, game: Game):
        sound.menu_select.play()
        match game.active_menu.options.lines[game.active_menu.current_selection]:
            case "Restart" | "Start game" | "New game":
                game.mode = "game"
                game.level.restart_game()
            case "Continue":
                game.mode = "game"
            case "Exit":
                game.running = False
            case "Next level":
                game.mode = "game"
                game.level.start_next()
            case "How to play" | "Back to controls":
                game.active_menu = Menu.create(["Controls", "W,A,S,D: control the ship", "  and navigate the menu", "SPACE: shoot bullets", "LEFT SHIFT: activate shield", "Left click: drop missile", "RETURN: pause the game","Escape: end the game"],
                                        ["Item list","Go back"])
            case "Item list" | "Previous items":
                game.active_menu = Menu.create(["Item list",
                                    [pygame.image.load("images/item/bullets_buff.png"), " upgrades your bullets"],
                                    [pygame.image.load("images/item/ship_buff.png"), " upgrades your ship"],
                                    [pygame.image.load("images/item/hp_plus.png"), f" gives back {ITEM.HP_PLUS.effect} energy"],
                                    [pygame.image.load("images/item/invert_controls.png"), f" inverts controls for {ITEM.INVERT_CONTROLS.duration}s"],
                                    [pygame.image.load("images/item/magnet.png"), " attracts items to you"],
                                    [pygame.image.load("images/item/score_buff.png"), f" score multiplier {ITEM.SCORE_BUFF.effect} for {ITEM.SCORE_BUFF.duration}s"]],
                                    ["More items", "Back to controls","Back to menu"])
            case "More items":
                game.active_menu = Menu.create(["Item list",
                                    [pygame.image.load(f"images/item/life_plus.png"), " ", pygame.image.load(f"images/item/life_minus.png"), " gives or takes a life"],
                                    [pygame.image.load(f"images/item/size_plus.png"), " ", pygame.image.load(f"images/item/size_minus.png"), f" increases or decreases ship size for {ITEM.SIZE_PLUS.duration}s"],
                                    [pygame.image.load(f"images/item/speed_buff.png"), " ", pygame.image.load(f"images/item/speed_nerf.png"), f" increases or decreases ship speed {ITEM.SPEED_BUFF.duration}s"],
                                    [pygame.image.load(f"images/item/shield.png"), f" increases shield timer by {ITEM.SHIELD.effect}s,"],
                                    "use it to reflect enemies and bullets.",
                                    [pygame.image.load(f"images/item/missile.png"), " gives an extra missile."],
                                    "They are strong, use them wisely!"],
                                    ["Previous items", "Back to controls","Back to menu"])
            case "Highscores":
                game.active_menu = Menu.create(["Highscores", "Do you think you can beat them?"],
                                                            ["Go back", "Delete high scores"],
                                                            highscores = game.highscores)
            case "Delete high scores":
                game.highscores.load_default_highscores()
                game.active_menu = Menu.create(["Highscores", "Do you think you can beat them?"],
                                                            ["Go back", "Delete high scores"],
                                                            highscores = game.highscores)
            case "Buy Premium":
                game.active_menu = Menu.create(["Haha", "Did you believe there", "is a premium version?"],
                                        ["Go back"])
            case "Credits":
                game.active_menu = Menu.create(["Credits", "Programmed with pygame", "Sprites and sound effects from",
                                        "pixabay.com, craftpix.net,", "opengameart.net and Google Gemini", "", "And thank you for beta testing!"],
                                        ["Go back"])
            case "Check high scores":
                game.score_rank = game.highscores.highscore_rank(game.level.ship.score)
                if game.score_rank is not None:
                    pygame.mixer.stop()
                    sound.new_highscore.play()
                    game.highscores.insert_score(name=game.player_name, score=game.level.ship.score, rank=game.score_rank)
                    game.mode = "enter name"
                else:
                    game.active_menu = Menu.create(["No new high score!", "Your score was too low,", "maybe next time!"], ["OK"],
                                                    highscores = game.highscores)
            case _:
                game.active_menu = Menu.create_main_menu(game)