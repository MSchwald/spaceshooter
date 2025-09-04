import pygame, sys
from image import Image
from sprite import Sprite

pygame.init()

screen = pygame.display.set_mode((1600,900))

frames = [Image.load(f"images/bullet/explosion{n}.png") for n in range(6)]

explosion = Sprite(frames=frames, animation_type="pingpong", fps=3)
clock = pygame.time.Clock()
t=0
while True:
    screen.fill((0,0,0))
    dt = clock.tick(10)
    explosion.update(dt)
    #print(explosion.timer)
    explosion.blit(screen)

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


