import pygame, sys
from image import Image
from sprite import Sprite


pygame.init()


screen = pygame.display.set_mode((1600,900))
#1: bilder 1-14
#2: bilder3-16
frames = [Image.load(f"astroid_2/00{str(100+n+1)[1:]}.png") for n in range(3,17)]

asteroid = Sprite(frames=frames, animation_type="loop", fps=5)
clock = pygame.time.Clock()
t=0
while True:
    screen.fill((0,0,0))
    dt = clock.tick(10)
    asteroid.update(dt)
    #print(explosion.timer)
    asteroid.blit(screen)

    pygame.display.flip()


    for event in pygame.event.get():
            # Clicking the 'X' of the window ends the game
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    n = max(0,n-1)
                if event.key == pygame.K_RIGHT:
                    n = min(45,n+1)


