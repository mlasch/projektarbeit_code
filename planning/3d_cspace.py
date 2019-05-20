#!/usr/bin/env python3

import math

from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection, Line3DCollection
import matplotlib.colors as colors
import matplotlib.pyplot as plt

class Vertex:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return "<V({},{})>".format(self.x, self.y)

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

class Obstacle:
    def __init__(self, vertexes=None):
        if vertexes:
            self.vertexes = vertexes
        else:
            self.vertexes = []

    def __iter__(self):
        return iter(self.vertexes)

    def __getitem__(self, key):
        return self.vertexes[key]

    def get_edges(self):
        pass

    def cspace(self, other):
        S = []

        # 1. step calculate minkowsky sum
        for vertex1 in self.vertexes:
            for vertex2 in other.vertexes:
                S.append(Vertex(vertex1.x + vertex2.x, vertex1.y + vertex2.y))

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

        return P

class Robot(Obstacle):
    def __init__(self, vertexes, pos, dir):
        self.pos = pos
        self.dir = dir

        super().__init__(vertexes)

    def turn(self, theta):
        for vertex in self.vertexes:
          x = math.cos(theta)*vertex.x - math.sin(theta)*vertex.y;
          y = math.sin(theta)*vertex.x + math.cos(theta)*vertex.y;

          vertex.x = x
          vertex.y = y

if __name__ == "__main__":
    op1 = Vertex(3,3)
    op2 = Vertex(3,4)
    op3 = Vertex(4,3)

    rp1, rp2, rp3, rp4, rp5 = Vertex(-1, -1), Vertex(1, -1), Vertex(1, 1), Vertex(0, 2), Vertex(-1, 1)

    obstacle = Obstacle([op1,op2,op3])
    obstacle2 = Obstacle([Vertex(8,0), Vertex(8,10), Vertex(8.1,10), Vertex(8.1,0)])

    init_theta = 0
    robot = Robot([rp1, rp2, rp3, rp4, rp5], Vertex(0,0), init_theta)

    ax = Axes3D(plt.figure(figsize=(6.4*1.8, 4.8*1.8)))

    poly3d = Poly3DCollection([[(v.x, v.y, init_theta) for v in robot]])
    poly3d.set_color('green')
    ax.add_collection3d(poly3d)

    obstacles = [obstacle, obstacle2]
    for theta in range(0, 360//60):
        theta *= 60
        robot.turn(theta)
        for obst in obstacles:

            cspace = obst.cspace(robot)
            # ax.scatter(*zip(*[(v.x, v.y, init_theta) for v in cspace]))
            poly3d = Poly3DCollection([[(v.x, v.y, theta) for v in cspace]], alpha=0.2)
            #poly3d.set_color(colors.rgb2hex((0,0,1)))
            poly3d.set_edgecolor('k')
            ax.add_collection3d(poly3d)

            polygon = []
            for vertex in obst:
                polygon.append((vertex.x, vertex.y, theta))

            poly3d = Poly3DCollection([polygon])
            poly3d.set_color(colors.rgb2hex((1,0,0)))

            ax.add_collection3d(poly3d)

    ax.set_xlim3d(-2, 10)
    ax.set_ylim3d(-2,10)
    ax.set_zlim3d(0,360)
    #ax.add_collection3d(Poly3DCollection(model))
    plt.show()

    # for angle in range(0, 360):
    #     ax.view_init(30, angle)
    #     plt.draw()
    #     plt.pause(.001)
