import pygame

pygame.display.init()

# Go into fullscreen mode with the current display settings of the player
info = pygame.display.Info()
display_w, display_h = info.current_w, info.current_h
display_size = display_w, display_h

#Fix a maximal surface "screen" on the display with following width:height ratio
desired_ratio = (16,9)
dw,dh = desired_ratio
ratio = dh*display_w-dw*display_h

if ratio == 0:
    # display has the desired ratio, no padding necessary
    screen_w, screen_h = display_w, display_h
    padding_w, padding_h = 0, 0  
elif ratio > 0:
    # display width is too big
    screen_w, screen_h = dw * display_h // dh, display_h
    padding_w, padding_h = (display_w - screen_w) // 2, 0
else:
    # display height is too big
    screen_w, screen_h = display_w, display_w * dh // dw
    padding_w, padding_h = 0, (display_h - screen_h) // 2

print("screen:", screen_w, screen_h)
print("padding:", padding_w, padding_h)
screen = pygame.Surface((screen_w,screen_h))
screen_rect = pygame.Rect(padding_w,padding_h,screen_w,screen_h)

def blit_screen_on_display():
    display.fill((100,100,100))  # grauer Hintergrund
    #display.blit(screen, screen_rect)
    # Debug: roten Rahmen ums Spielfeld
    pygame.draw.rect(display, (200,0,0), screen_rect, 4)
    display.blit(screen, screen_rect)
    