import pygame
import sys
from Board import Game
    
pygame.init()

# set up the window
size = (640, 640)
screen = pygame.display.set_mode(size)
pygame.display.set_caption("Chess Game")

# set up the board
board = pygame.Surface((640, 640)) # Each tile is 80x80
board.fill((255, 206, 158))

# add the board to the screen
screen.blit(board, (0, 0))
pygame.display.flip()


first = Game()
first.display()

playing = True
while playing:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()   
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            first.handle_mouse_down(pygame.mouse.get_pos())
        elif event.type == pygame.MOUSEBUTTONUP:
            first.handle_mouse_up(pygame.mouse.get_pos())
    
    first.draw(screen)
    pygame.display.flip()
    