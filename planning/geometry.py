#!/usr/bin/env python3

import math

from pprint import pprint
from copy import copy, deepcopy

class Vertex:
    def __init__(self, x, y, neighbors=None):
        self.x = x
        self.y = y

        if not neighbors:
            self.neighbors = []
        else:
            self.neighbors = neighbors

    def add_neighbor(self, neighbor):
        if neighbor not in self.neighbors:
            self.neighbors.append(neighbor)

    def __repr__(self):
        return "<V({:0.2f},{:0.2f})>".format(self.x, self.y)


class Graph:
    def __init__(self, nodes=None):
        if nodes:
            self.nodes = nones
        else:
            self.nodes = []

    def add_node(self, node):
        if node not in self.nodes:
            self.nodes.append(node)

    @staticmethod
    def visibility_graph(map, start=None, end=None):
        graph = Graph()

        # naive approach, not very performant!
        for obstacle in map:
            for obstacle2 in map:
                if obstacle == obstacle2:
                    # add vertexes of polygon itself
                    for edge in obstacle.edges:
                        graph.add_node(edge.p1)
                        edge.p1.add_neighbor(edge.p2)
                        edge.p2.add_neighbor(edge.p1)
                    continue

                for vertex in obstacle:
                    for vertex2 in obstacle2:
                        if vertex == vertex2:
                            continue

                        line = Edge(vertex, vertex2)
                        intersect = False
                        for obstacle3 in map:
                            if not obstacle3.check_line(line):
                                # line intersects
                                intersect = True
                                break

                        if not intersect:
                            vertex.add_neighbor(vertex2)
                            graph.add_node(vertex)

        return graph

    def __len__(self):
        return len(self.nodes)

    def __repr__(self):
        _str = "<{} nodes=".format(self.__class__.__name__)
        for node in self.nodes:
            _str += "{}".format(node)
        return _str+">"


class Edge:
    def __init__(self, p1=None, p2=None):
        if p1:
            self.p1 = p1
        else:
            self.p1 = Vertex(0,0)

        if p2:
            self.p2 = p2
        else:
            self.p2 = Vertex(0,0)

    def intersect(self, other):
        # more info https://en.wikipedia.org/wiki/Line%E2%80%93line_intersection
        den = ((self.p1.x-self.p2.x)*(other.p1.y-other.p2.y)) - ((self.p1.y-self.p2.y)*(other.p1.x-other.p2.x))
        if den == 0:
            # parallel or colinear
            # *TODO* handle colinear case
            return False

        t =  ((self.p1.x - other.p1.x) * (other.p1.y - other.p2.y) - (self.p1.y - other.p1.y) * (other.p1.x - other.p2.x)) / den
        u = -((self.p1.x -  self.p2.x)  * (self.p1.y - other.p1.y) - (self.p1.y -  self.p2.y) * ( self.p1.x - other.p1.x)) / den

        if u < 1 and u > 0 and t < 1 and t > 0:
            return (self.p1.x+t*(self.p2.x-self.p1.x), self.p1.y+t*(self.p2.y-self.p1.y))
        else:
            return False

    def __repr__(self):
        return "<edge {}->{}>".format(self.p1, self.p2)


class Obstacle:
    def __init__(self, vertexes=None):
        if vertexes:
            self.vertexes = vertexes
        else:
            self.vertexes = []

    @property
    def edges(self):
        v1 = self.vertexes[-1]
        for v2 in self.vertexes:
            #if v1 != None:
            yield Edge(v1, v2)
            v1 = v2

    def __iter__(self):
        return iter(self.vertexes)

    def __getitem__(self, key):
        return self.vertexes[key]

    def cspace(self, other):
        S = []

        # 1. step calculate minkowsky sum
        for vertex1 in self:
            for vertex2 in other:
                S.append(Vertex(vertex1.x + vertex2.x, vertex1.y + vertex2.y))

        # 2. step form convex hull
        S.sort(key=lambda v: v.x)
        P = [S[0]]
        next_p = None

        start_p = S[0]
        while (next_p != P[0]):
            next_p = None
            for check_p in S:

                if next_p == None:
                    next_p = check_p
                else:
                    position = (next_p.x - start_p.x) * (check_p.y - start_p.y) - (next_p.y - start_p.y) * (check_p.x - start_p.x)

                    if next_p == start_p or position < 0:
                        next_p = check_p

            P.append(next_p)

            start_p = next_p

        # 3. remove intermediate vertexes

        return P

    def check_line(self, line):
        for edge in self.edges:
            if line.intersect(edge):
                return False
        # return True if no edge of the polygon intersect with the line
        return True

class Robot(Obstacle):
    def __init__(self, vertexes, pos, dir):
        self.pos = pos
        self.dir = dir

        self._init_vertexes = deepcopy(vertexes)
        super().__init__(vertexes)

    def turn(self, theta):

        for i, vertex in enumerate(self._init_vertexes):
            radian = theta/360*math.pi*2
            x = math.cos(radian)*vertex.x - math.sin(radian)*vertex.y;
            y = math.sin(radian)*vertex.x + math.cos(radian)*vertex.y;

            self.vertexes[i].x = x
            self.vertexes[i].y = y
