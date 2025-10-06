import pygame, sys
from menu import Menu
from settings import Color

pygame.init()

clock = pygame.time.Clock()

screen = pygame.display.set_mode((1900,1000)) 
path = "images/alien/ufo.png"
colorkey = (0,0,0)

raw_image = pygame.image.load(path)
if colorkey != (0,0,0):
    raw_image.set_colorkey((0,0,0))
    temp = raw_image.copy()
    temp.set_colorkey(colorkey)
    mask = pygame.mask.from_surface(temp)
    mask.invert() #the inverted mask covers all transparent pixels
    mask = mask.connected_component() #this component is exactly the boundary
    mask.invert() #its inverse is the mask of the actual figure on the image
    raw_image = mask.to_surface(surface=raw_image, setcolor=None)
bounding_rect = raw_image.get_bounding_rect()
cropped = pygame.Surface(bounding_rect.size, pygame.SRCALPHA)
cropped.blit(raw_image,(0,0), bounding_rect)
#surface.blit(cropped,(0,0),bounding_rect)


while True:
    
    screen.fill(Color.WHITE)
    pygame.display.flip()


    for event in pygame.event.get():
            # Clicking the 'X' of the window ends the game
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    sys.exit()


