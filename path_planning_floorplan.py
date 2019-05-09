#!/usr/bin/env python3
import argparse
import pygame
import math
import time

from planning.floorplan import Floorplan

FPS = 30

# colors
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
DARKBLUE = (0, 0, 160)
GREY = (100, 100, 100)
DARKGREY = (50, 50, 50)
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

    floor = Floorplan('CAD Files/polygon_convex_example.dxf')
    #floor = Floorplan('CAD Files/li27_example.dxf')
    #xmin, xmax, ymin, ymax = floor.get_boundary()

    width = 1000
    width, height = floor.set_width(width)

    screen = pygame.display.set_mode((math.ceil(width), math.ceil(height)))

    pygame.display.set_caption("Path Planning Polygon Demo")
    clock = pygame.time.Clock()

    graph_iter = iter(floor.generate_graph(screen))
    #graph = []
    running = True
    edge = None

    for i in floor.generate_graph(screen):
        pass

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONUP:
                pos = pygame.mouse.get_pos()
                try:
                    #line,edge,intersect = next(graph_iter)
                    if intersect:
                        print("INTERSECT!")
                    else:
                        print("no intersection")
                except StopIteration:
                    pass

        screen.fill(GREY)

        #pygame.draw.circle(screen, GREEN, map_.current_pos, 10)
        #pygame.draw.circle(screen, RED, map_.dest_pos, 10)

        for polygon in floor.polygons:
            pygame.draw.polygon(screen, DARKGREY, list(map(lambda x: floor.scale_xy(*x), polygon.vertexes)))

        for graph_line in floor.graph:
            pygame.draw.line(screen, YELLOW, floor.scale_xy(*graph_line.start), floor.scale_xy(*graph_line.end))

        if edge:
            if intersect:
                color = RED
            else:
                color = GREEN
            pygame.draw.line(screen, color, floor.scale_xy(*line.start), floor.scale_xy(*line.end))
            pygame.draw.line(screen, YELLOW, floor.scale_xy(*edge.start), floor.scale_xy(*edge.end))

        pygame.display.flip()  # turn double buffer

        clock.tick(FPS)

    pygame.quit()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Path Planning Demo')
    args = parser.parse_args()

    main()
