#!/usr/bin/env python3

import pygame
import argparse
import math

FPS = 30

# colors
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
DARKBLUE = (0, 0, 160)
GREY = (100, 100, 100)
YELLOW = (0xF7, 0xCA, 0x18)

class Obstacle(object):
    def __init__(self, points):
        self.points = points

class Map(object):
    def __init__(self, obstacles=None):
        if obstacles == None:
            self.obstacles = []
        else:
            self.obstacles = obstacles

        self.current_pos = (100,100)
        self.dest_pos = (400, 500)

def main():
    from pprint import pprint
    pygame.init()
    pygame.mixer.quit() #workaround for https://github.com/pygame/pygame/issues/331  
    
    width = 800
    height = 600
    
    screen = pygame.display.set_mode((width, height)) 

    pygame.display.set_caption("Path Planning Polygon Demo")
    clock = pygame.time.Clock()

    map_ = Map()

    running = True
    redraw = True

    obj1 = Obstacle([(400,100), (420, 100), (420, 400), (150, 400), (150, 380), (400, 380)])

    while running: 
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONUP:
                pos = pygame.mouse.get_pos()
    
        screen.fill(BLACK)
        
        pygame.draw.circle(screen, GREEN, map_.current_pos, 10)
        pygame.draw.circle(screen, RED, map_.dest_pos, 10)
        pygame.draw.polygon(screen, GREY, obj1.points)



        pygame.display.flip()  # turn double buffer

        clock.tick(FPS)

    pygame.quit()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Path Planning Demo')
    args = parser.parse_args()

    main()


