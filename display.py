import pygame

class Display:
    """Manage fullscreen rendering and grid layout for the game.

    This class handles adapting the game surface to the player's screen resolution,
    keeping the desired aspect ratio, centering the screen, and computing a
    grid for consistent positioning of sprites.

    display: pygame.Surface | None
        The actual fullscreen display surface.
    screen: pygame.Surface | None
        The internal game surface (possibly smaller than `display` to preserve aspect ratio)
        with automatically set parameters screen_rect, screen_width, screen_height, screen_size.
        Gets subdivided into a rectangle of square grid cells with parameters
        grid: tuple[int, int] and grid_width.
        Gets padded for rendering on the screen with int parameters padding_w, padding_h"""
    display: pygame.Surface | None = None
    screen: pygame.Surface | None = None
    screen_rect: pygame.Rect | None = None
    screen_width: int = 0
    screen_height: int = 0
    screen_size: tuple[int, int] = (0, 0)
    grid: tuple[int, int] = (0, 0)
    grid_width: int = 0
    padding_w: int = 0
    padding_h: int = 0

    def __init__(self, screen_size: tuple[int, int], screen_grid: tuple[int, int]):
        """Initialize the internal game surface 'screen' with given aspect ratio and grid layout"""
        pygame.display.init()
        info = pygame.display.Info()
        max_width, max_height = info.current_w, info.current_h
        Display.display = pygame.display.set_mode((max_width, max_height), pygame.FULLSCREEN)

        w, h = screen_size
        
        ratio = h * max_width - w * max_height

        if ratio == 0:
            # display has the desired ratio, no padding necessary
            screen_w, screen_h = max_width, max_height
            Display.padding_w, Display.padding_h =  0, 0  
        elif ratio > 0:
            # display is too wide
            screen_w, screen_h = w * max_height // h, max_height
            Display.padding_w, Display.padding_h = (self.width - screen_w) // 2, 0
        else:
            # display is too high
            screen_w, screen_h = max_width, max_width * h // w
            Display.padding_w, Display.padding_h = 0, (max_height - screen_h) // 2

        Display.screen = pygame.Surface((screen_w,screen_h))
        Display.screen_rect = pygame.Rect(Display.padding_w, Display.padding_h, screen_w, screen_h)
        Display.screen_width, Display.screen_height = screen_w, screen_h
        Display.screen_size = (screen_w, screen_h)
        Display.grid = screen_grid
        Display.grid_width = Display.screen_width // screen_grid[0]

    @classmethod
    def init(cls, screen_size: tuple[int, int], screen_grid: tuple[int, int]) -> pygame.Surface:
        """Convenience method to initialize the display and ontain the internal game surface."""
        cls(screen_size, screen_grid)
        return cls.screen

    @classmethod
    def update(cls, padding_color: tuple):
        """Blit internal game surface centered on the fullscreen display"""
        cls.display.fill(padding_color)
        cls.display.blit(cls.screen, cls.screen_rect)
        pygame.display.flip()

    @classmethod
    def grid_rect(cls, x_min: int = 0, y_min: int = 0,
                width: int = grid[0], height: int = grid[1]) -> pygame.Rect:
        """Return a rectangle aligned to the initialized display grid."""
        return pygame.Rect([x_min * cls.grid_width, y_min * cls.grid_width,
                            width * cls.grid_width, height * cls.grid_width])
        

