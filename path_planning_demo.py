#!/usr/bin/env python3

import pygame
import argparse

FPS = 30

# colors
BLACK = (0, 0, 0)

def main(width, height):
    pygame.init()
    
    screen = pygame.display.set_mode((width, height)) 

    pygame.display.set_caption("Path Planning Demo")
    clock = pygame.time.Clock()

    running = True

    while running:
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill(BLACK)
        
        pygame.display.flip()  # turn double buffer

        clock.tick(FPS)

    pygame.quit()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Path Planning Demo')
    parser.add_argument('width', metavar='W', type=int,
            help='Number of horizontal nodes')
    parser.add_argument('height', metavar='H', type=int,
            help='Number of vertival nodes')

    args = parser.parse_args()

    main(args.width, args.height)


