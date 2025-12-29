from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.core import Game, Level, Highscores

import pygame
from .text import Layout, Text
from src.utils import Display, Sound
from src.settings import COLOR, KEY, SCREEN, FONT, MENU, LEVEL_STATUS, GAME_MODE, HIGHSCORES, PATH
from src.templates import ITEM

class Menu():
    """Manage creation and navigation of menus consisting of a header surface
    and a list of options. Header surface can be rendered from a given text."""
    
    @classmethod
    def init_settings(cls):
        """Initiate menu formating scaled according to the user's display settings"""
        pygame.font.init()
        cls.menu_font_size = int(FONT.MENU_SIZE * Display.screen_width / SCREEN.WIDTH)
        cls.text_font_size = int(FONT.TEXT_SIZE * Display.screen_width / SCREEN.WIDTH)
        cls.menu_font = pygame.font.Font(FONT.MENU, cls.menu_font_size)
        cls.text_font = pygame.font.Font(FONT.TEXT, cls.text_font_size)
        cls.boundary_size = int(MENU.BOUNDARY_SIZE * Display.screen_width / SCREEN.WIDTH)
        cls.title_distance = int(MENU.TITLE_DISTANCE * Display.screen_width / SCREEN.WIDTH)
        cls.line_distance = int(MENU.LINE_DISTANCE * Display.screen_width / SCREEN.WIDTH)
        cls.init_info_menus()

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
        """Used for highlighting the selected option when rendering the menu."""
        self.options.rendered_lines = self.inactive_options.rendered_lines[:]
        self.options.rendered_lines[self.current_selection] = self.highlighted_options.rendered_lines[self.current_selection]

    def render(self) -> pygame.Surface:
        """Renders the the menu as a pygame.Surface"""
        rendered_options = self.options.render("center",Menu.line_distance, padding_color=COLOR.BLUE, center_title=False)
        rendered_menu = Layout.align_surfaces([self.header_surface,rendered_options], orientation="vertical", spacing = Menu.title_distance, padding_size = Menu.boundary_size//2, padding_color = COLOR.BLUE)
        return Layout.pad_surface(rendered_menu, padding_size=Menu.boundary_size // 2, padding_color=COLOR.RED)

    def blit(self, screen: pygame.Surface | None = None):
        """Blits the menu with the current selection highlighted onto the screen"""
        screen = screen or Display.screen
        screen.blit(self.rendered_menu, ((
            screen.get_width()-self.w)//2, (screen.get_height()-self.h)//2))

    def move_selection(self, event_key):
        """Navigate through the menus otion according to user's input"""
        Sound.menu_move.play()
        self.current_selection = (
            (self.current_selection + {KEY.UP : -1, KEY.DOWN : 1}[event_key]) % len(self.options.lines)
        )
        self.highlight()
        self.rendered_menu = self.render()

    @classmethod
    def create(cls, message: list[str], options: list[str],
                    current_selection: int = 0, highscores: Highscores | None = None) -> Menu:
        """Creates a menu from a given title message and options,
        allows for showing high sores in between"""
        if highscores is not None:
            message += [""]
        text = Text(message, Menu.text_font, COLOR.WHITE, COLOR.BLUE)
        rendered_message = text.render("left", Menu.line_distance, padding_color=COLOR.BLUE, title_distance=Menu.title_distance)
        if highscores is not None:
            # Render high scores as a two columned table
            players = Text(highscores.players, Menu.menu_font, COLOR.WHITE, COLOR.BLUE)
            scores = Text(highscores.scores, Menu.menu_font, COLOR.WHITE, COLOR.BLUE)
            rendered_players = players.render("left", Menu.line_distance, padding_color=COLOR.BLUE, center_title=False)
            rendered_scores = scores.render("right", Menu.line_distance, padding_color=COLOR.BLUE, center_title=False)
            table = Layout.align_surfaces([rendered_players,rendered_scores],orientation="horizontal",spacing=Menu.title_distance,padding_color=COLOR.BLUE)
            header_surface = Layout.align_surfaces([rendered_message,table],orientation="vertical",spacing=Menu.line_distance,padding_color=COLOR.BLUE)
        else:
            header_surface = rendered_message
        return Menu(header_surface, options, current_selection=current_selection)

    @classmethod
    def create_main_menu(cls, game: Game) -> Menu:
        """Return the correct Main / Pause menu in each game situation."""
        match game.player_name, game.level.status:
            case _, LEVEL_STATUS.RUNNING:
                message, options = ["Pause"], ["Continue", "Restart"]
            case "", LEVEL_STATUS.GAME_WON:
                message, options = ["Good game!", "Do you want to play again?"], ["New game"]
            case _, LEVEL_STATUS.GAME_WON:
                message, options = [f"Good game, {game.player_name}!", "Do you want to play again?"], ["New game"]
            case "", LEVEL_STATUS.GAME_OVER:
                message, options = ["Game over!","You ran out of lives!", "Do you want to play again?"], ["New game"]
            case _, LEVEL_STATUS.GAME_OVER:
                message, options = ["Game over!", f"{game.player_name}, do you want to play again?"], ["New game"]
            case "", LEVEL_STATUS.START:
                message, options = ["Space invaders", "Navigate menu with W,S","and pressing RETURN."], ["Start game"]
            case _, LEVEL_STATUS.START:
                message, options = [f"Welcome back, {game.player_name}!"], ["Start game"]
        default_options = ["How to play","Highscores", "Buy Premium", "Credits", "Exit"]
        return Menu.create(message, options + default_options)

    @classmethod
    def create_level_menu(cls, level: Level) -> Menu:
        """Return an info menu when a level ends according to the given level status."""
        if level.status in (LEVEL_STATUS.LEVEL_SOLVED, LEVEL_STATUS.GAME_WON, LEVEL_STATUS.GAME_OVER):
            level.play_status_sound()
            match level.status:
                case LEVEL_STATUS.LEVEL_SOLVED:
                    return Menu.create([f"Level {level.number} solved!",
                                f"In level {level.number+1}, you have to", f"{level.goals[level.number+1]}"],
                                ["Next level"])
                case LEVEL_STATUS.GAME_WON:
                    return Menu.create(["Congratulations!", "You have finished", "all available levels!"],
                                ["Check high scores"])
                case LEVEL_STATUS.GAME_OVER: 
                    return Menu.create(["Game over!","You ran out of lives!"],
                                ["Check high scores"])

    @classmethod
    def create_enter_name_menu(cls, game: Game) -> Menu:
        """Create the menu for entering the player's name into the high score list."""
        return Menu.create(["Congratulations!", f"Your score ranks on place {game.score_rank+1}.",
                            "Please enter your name and press RETURN."],
                            [f"Name: {game.player_name}"],
                            highscores = game.highscores)

    def handle_input(self, game: Game, event):
        """Handles entering the name into the high score list upon user's input"""
        if event.type == pygame.KEYDOWN:
            if event.unicode in game.highscores.allowed_chars and len(game.player_name) < HIGHSCORES.MAX_NAME_LENGTH:
                game.player_name += event.unicode
            elif event.key == KEY.BACK:
                game.player_name = game.player_name[:-1]
            elif event.key == KEY.START:
                    game.highscores.save()
                    game.active_menu = Menu.create_main_menu(game)
                    game.mode = GAME_MODE.MENU

    @classmethod
    def init_info_menus(cls):
        """Informational Menus in the game get rendered only once"""
        cls.CONTROLS = Menu.create(["Controls",
                                "W,A,S,D: control the ship",
                                "  and navigate the menu",
                                "SPACE: shoot bullets",
                                "LEFT SHIFT: activate shield",
                                "Left click: drop missile",
                                "RETURN: pause the game","Escape: end the game"],
                                options = ["Item list", "Go back"])
        cls.ITEM_LIST1 = Menu.create(["Item list",
                                [pygame.image.load(PATH.ITEM / "bullets_buff.png"), " upgrades your bullets"],
                                [pygame.image.load(PATH.ITEM / "ship_buff.png"), " upgrades your ship"],
                                [pygame.image.load(PATH.ITEM / "hp_plus.png"), f" gives back {ITEM.HP_PLUS.effect} energy"],
                                [pygame.image.load(PATH.ITEM / "invert_controls.png"), f" inverts controls for {ITEM.INVERT_CONTROLS.duration}s"],
                                [pygame.image.load(PATH.ITEM / "magnet.png"), " attracts items to you"],
                                [pygame.image.load(PATH.ITEM / "score_buff.png"), f" score multiplier {ITEM.SCORE_BUFF.effect} for {ITEM.SCORE_BUFF.duration}s"]],
                                options = ["More items", "Back to controls", "Back to menu"])
        cls.ITEM_LIST2 = Menu.create(["Item list",
                                [pygame.image.load(PATH.ITEM / "life_plus.png"), " ", pygame.image.load(PATH.ITEM / "life_minus.png"), " gives or takes a life"],
                                [pygame.image.load(PATH.ITEM / "size_plus.png"), " ", pygame.image.load(PATH.ITEM / "size_minus.png"), f" increases or decreases ship size for {ITEM.SIZE_PLUS.duration}s"],
                                [pygame.image.load(PATH.ITEM / "speed_buff.png"), " ", pygame.image.load(PATH.ITEM / "speed_nerf.png"), f" increases or decreases ship speed {ITEM.SPEED_BUFF.duration}s"],
                                [pygame.image.load(PATH.ITEM / "shield.png"), f" increases shield timer by {ITEM.SHIELD.effect}s,"],
                                "use it to reflect enemies and bullets.",
                                [pygame.image.load(PATH.ITEM / "missile.png"), " gives an extra missile."],
                                "They are strong, use them wisely!"],
                                options =["Previous items", "Back to controls", "Back to menu"])
        cls.PREMIUM = Menu.create(["Haha",
                                "Did you believe there",
                                "is a premium version?"],
                                options = ["Go back"])
        cls.CREDITS = Menu.create(["Credits",
                                "Programmed with pygame",
                                "Sprites and sound effects from",
                                "pixabay.com, craftpix.net,",
                                "opengameart.net and Google Gemini",
                                "",
                                "And thank you for beta testing!"],
                                options = ["Go back"])

    @classmethod
    def choose_current_selection(cls, game: Game):
        """Triggers the right game effects or opens new Menu
        when player chooses an option of a menu."""
        Sound.menu_select.play()
        match game.active_menu.options.lines[game.active_menu.current_selection]:

            # Menu options that start or exit the game
            case "Restart" | "Start game" | "New game":
                game.mode = GAME_MODE.GAME
                game.level.restart_game()
            case "Continue":
                game.mode = GAME_MODE.GAME
            case "Exit":
                game.running = False
            case "Next level":
                game.mode = GAME_MODE.GAME
                game.level.start_next()

            # Menu options to browse the main menu
            case "How to play" | "Back to controls":
                game.active_menu = Menu.CONTROLS
            case "Item list" | "Previous items":
                game.active_menu = Menu.ITEM_LIST1
            case "Buy Premium":
                game.active_menu = Menu.PREMIUM
            case "Credits":
                game.active_menu = Menu.CREDITS
            case "More items":
                game.active_menu = Menu.ITEM_LIST2

            # High score menus
            case "Highscores":
                game.active_menu = Menu.create(["Highscores",
                                                "Do you think you can beat them?"],
                                                options = ["Go back", "Delete high scores"],
                                                highscores = game.highscores)
            case "Delete high scores":
                game.highscores.load_default_highscores()
                game.active_menu = Menu.create(["Highscores",
                                                "Do you think you can beat them?"],
                                                options = ["Go back", "Delete high scores"],
                                                highscores = game.highscores)
            case "Check high scores":
                game.score_rank = game.highscores.highscore_rank(game.level.ship.score)
                if game.score_rank is not None:
                    pygame.mixer.stop()
                    Sound.new_highscore.play()
                    game.highscores.insert_score(name=game.player_name, score=game.level.ship.score, rank=game.score_rank)
                    game.mode = GAME_MODE.ENTER_NAME
                else:
                    game.active_menu = Menu.create(["No new high score!",
                                                    "Your score was too low,",
                                                    "maybe next time!"],
                                                    options = ["OK"],
                                                    highscores = game.highscores)
            case _:
                game.active_menu = Menu.create_main_menu(game)