import pygame
import sys

pygame.init()
window_size = (1280, 720)
window = pygame.display.set_mode(window_size)
pygame.display.set_caption('UFV WILDS')

BG = pygame.image.load('StreamingAssets/background.png')

# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Main game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    window.fill(WHITE)  # Fill the background with white
    pygame.display.flip()  # Update the display

pygame.quit()
sys.exit()
