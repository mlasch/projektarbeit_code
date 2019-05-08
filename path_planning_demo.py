#!/usr/bin/env python3

import pygame
import argparse
import math

from queue import PriorityQueue

FPS = 5
N_PIXEL = 20
BORDER = 4

# colors
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
DARKBLUE = (0, 0, 160)
GREY = (100, 100, 100)
YELLOW = (0xF7, 0xCA, 0x18)

def pos_to_node(pos, graph):
    x, y = pos
    
    print()
    row = math.ceil(y/N_PIXEL) - 1
    col = math.ceil(x/N_PIXEL) - 1

    return graph.get_node(row, col)


class Node():
    NORMAL = 0
    START = 1
    END = 2
    
    def __init__(self, row, col, neighbors=None, state=None):
        self.row = row
        self.col = col

        if not neighbors:
            self.neighbors = []
        else:
            self.neighbors = neighbors
        
        if not state:
            self.state = self.NORMAL
        else:
            self.state = state

        self.cost = math.inf
        self.visited = False        

    def add_neighbor(self, neighbor):
        self.neighbors.append(neighbor)

    def clear_neighbors(self):
        """
        Clear incoming edges from neighbors
        """
        for neighbor in self.neighbors:
            neighbor.erase_edge(self)
        self.neighbors = []

    def erase_edge(self, node):
        for idx, neighbor in enumerate(self.neighbors):
            if node == neighbor: 
                print(f"ERASE outging edge from {self} ->  {neighbor}")
                self.neighbors.pop(idx)

    def get_closest_neighbor(self):
        return sorted(self.neighbors)[0]

    def __lt__(self, other):
        return self.cost < other.cost

    def __repr__(self):
        ret = '<node({},{},cost={}) neighbors='.format(self.row, self.col, self.cost)
        for neighbor in self.neighbors:
            ret += '({},{},cost={})'.format(neighbor.row, neighbor.col, neighbor.cost)

        return ret+'>'

class Graph():
    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols

        self.graph = []

        for row in range(self.rows):
            for col in range(self.cols):
                # new node
                node = Node(row, col)
                #print("CREATE", row, col)
                self.graph.append(node)
                #print("CURRENT max index", len(self.graph)-1)
                 
                # create bidirectional vertices between the nodes
                if col > 0:
                    #print("add vertical")
                    left = self.get_node(row, col-1)
                    #print("ADD from {} to {}".format(node, left))
                    node.neighbors.append(left)
                    left.neighbors.append(node)

                if row > 0:
                    #print("add horizontal")
                    top = self.get_node(row-1, col)
                    #print("ADD from {} to {}".format(node, top))
                    node.neighbors.append(top)
                    top.neighbors.append(node)

        # set start and endnode
        self.get_node(int(self.rows/2),int(self.cols/2)).state = Node.START
        self.get_node(int(self.rows/2+1),self.cols-2).state = Node.END

    def get_node(self, row, col):
        #print("ACCESS index ({},{})".format(row,col), self.rows * row + col)
        return self.graph[self.cols * row + col]

    def compute_path(self):
        visited = []

        # initialize
        for node in self.graph:
            if node.state == Node.START:
                node.cost = 0
                start_node = node
                node.visited = True
            elif node.state == Node.END:
                node.cost = math.inf
                node.visited = False
                end_node = node
            else:
                node.cost = math.inf
                node.visited = False

        pqueue = PriorityQueue()    # format (cost, node)
    
        pqueue.put(start_node)
        cnt = 0
        run = True
        print("START")
        while run:
            cnt += 1
            current_node = pqueue.get()
            print(current_node)
            for next_node in current_node.neighbors:
                if next_node.visited  == False:
                    if next_node.state == Node.END:
                        print("FOUND END after {} cycles".format(cnt))
                        run = False
                        break

                    print("visit node", next_node)

                    new_cost = current_node.cost + 1
                    print("increment cost to", new_cost)
                    next_node.visited = True


                    print(f"new cost{new_cost} current_cost: {current_node.cost}")
                    if new_cost < next_node.cost:
                        # update cost if smaller
                        next_node.cost = new_cost
                        print("set new cost", new_cost)

                    pqueue.put(next_node)

        
        reverse_node = next_node
        # get path
        reverse_path = []
        while reverse_node.state != Node.START:
            print(reverse_node)
            reverse_node = reverse_node.get_closest_neighbor()
            reverse_path.append(reverse_node)
       

        list.reverse(reverse_path)
        reverse_path.append(next_node)

        return reverse_path

    def __repr__(self):
        ret = ''

        for node in self.graph:
            ret += "{}\n".format(node)

        return ret

def main(rows, cols):
    from pprint import pprint
    from random import randint
    pygame.init()

    graph = Graph(rows, cols)

    width = cols*N_PIXEL+BORDER
    height = rows*N_PIXEL+BORDER
    
    screen = pygame.display.set_mode((width, height)) 

    pygame.display.set_caption("Path Planning Demo")
    clock = pygame.time.Clock()

    
    path = []
    running = True
    redraw = True

    while running:
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONUP:
                pos = pygame.mouse.get_pos()

                node = pos_to_node(pos, graph)
                node.clear_neighbors()
                
                path = graph.compute_path()

                redraw = True
                
                print(f"Pressed {pos} got {node}")

        if redraw:

            screen.fill(BLACK)
            for node in graph.graph:
                x = N_PIXEL*(node.col)+ BORDER
                y = N_PIXEL*(node.row)+ BORDER
                w = N_PIXEL-BORDER
                h = N_PIXEL-BORDER
                
                if len(node.neighbors) == 0:
                    color = GREY
                elif node.state == Node.START:
                    color = GREEN
                elif node.state == Node.END:
                    color = RED
                elif node.visited == True:
                    color = BLUE
                else:
                    color = DARKBLUE

                pygame.draw.rect(screen, color, [x, y, w, h], 0)
            
            node_list = []
            for node in path:
                node_list.append((N_PIXEL*(node.col + 1/2)+BORDER/2, 
                    N_PIXEL*(node.row + 1/2)+BORDER/2))

            if node_list:
                pygame.draw.lines(screen, YELLOW, False, node_list, 4)
            redraw = False
            pygame.display.flip()  # turn double buffer

        clock.tick(FPS)

    pygame.quit()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Path Planning Demo')
    parser.add_argument('rows', metavar='c', type=int,
            help='Number of vertical nodes')
    parser.add_argument('cols', metavar='r', type=int,
            help='Number of horizontal nodes')

    args = parser.parse_args()

    main(args.rows, args.cols)


