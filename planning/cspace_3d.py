#!/usr/bin/env python3

import math
import pdb
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection, Line3DCollection
import matplotlib.colors as colors
import matplotlib.pyplot as plt

from pprint import pprint
from copy import copy, deepcopy

from geometry import Vertex, Edge, Obstacle, Robot, Graph


if __name__ == "__main__":
    op1 = Vertex(3,3)
    op2 = Vertex(3,4)
    op3 = Vertex(4,3)

    obstacle = Obstacle([op1,op2,op3])
    obstacle1 = Obstacle([Vertex(8,0), Vertex(8,4), Vertex(8.1,4), Vertex(8.1,0)])
    obstacle2 = Obstacle([Vertex(8,6.5), Vertex(8,10), Vertex(8.1,10), Vertex(8.1,6.5)])

    init_theta = 0
    robot = Robot([ Vertex(-1, -1), Vertex(1, -1), Vertex(1, 1), Vertex(0, 2), Vertex(-1, 1)],
        Vertex(0,0), init_theta)

    ax = Axes3D(plt.figure(figsize=(6.4*1.8, 4.8*1.8)))

    INC = 180

    for theta in range(360//INC+1):
        theta *= INC
        robot.turn(theta)
        # print(theta)
        # print("ROBOT: {}, {}".format(len(robot.vertexes), len(robot._init_vertexes)))
        #
        # pprint(list(robot))

        poly3d = Poly3DCollection([[(v.x, v.y, theta) for v in robot]])
        poly3d.set_color(colors.rgb2hex((0.2, 1, 0.2, 0.7)))
        poly3d.set_edgecolor('k')
        ax.add_collection3d(poly3d)

    obstacles = [obstacle, obstacle1, obstacle2]

    cspace_map = [[] for i in range(360//INC+1)]

    for obst in obstacles:
        for i_angle, theta in enumerate(range(360//INC+1)):
            theta *= INC
            robot.turn(theta)

            cspace = Obstacle(obst.cspace(robot))
            cspace_map[i_angle].append(cspace)

            # ax.scatter(*zip(*[(v.x, v.y, init_theta) for v in cspace]))
            poly3d = Poly3DCollection([[(v.x, v.y, theta) for v in cspace]], alpha=0.7)
            poly3d.set_color(colors.rgb2hex((0.2,0.2,1,0.2)))
            poly3d.set_edgecolor('k')
            ax.add_collection3d(poly3d)

            # cspace.append(cspace[0])
            # if cspace_down:
            #     for i in range(max(len(cspace),len(cspace_down))-1):
            #         if i > len(cspace)-1:
            #             i_up =  len(cspace)-1
            #         else:
            #             i_up = i-1
            #         if i > len(cspace_down)-1:
            #             i_down = len(cspace_down)-1
            #         else:
            #             i_down = i-1
            #
            #         area = [(cspace_down[i_down].x, cspace_down[i_down].y, theta-INC),
            #                 (cspace_down[i_down-1].x, cspace_down[i_down-1].y, theta-INC),
            #                 (cspace[i_up-1].x, cspace[i_up-1].y, theta),
            #                 (cspace[i_up].x, cspace[i_up].y, theta)]
            #
            #         # area = [(cspace_down[i].x, cspace_down[i].y, theta-INC),
            #         #         (cspace_down[i-1].x, cspace_down[i-1].y, theta-INC),
            #         #         (cspace[i-1].x, cspace[i-1].y, theta),
            #         #         (cspace[i].x, cspace[i].y, theta)]
            #
            #         poly3d = Poly3DCollection([area], alpha=0.2)
            #         poly3d.set_edgecolor('k')
            #         ax.add_collection3d(poly3d)
            #
            #
            # cspace_down = deepcopy(cspace)

            polygon = []
            for vertex in obst:
                polygon.append((vertex.x, vertex.y, theta))

            poly3d = Poly3DCollection([polygon])
            poly3d.set_color(colors.rgb2hex((1,0,0)))

            ax.add_collection3d(poly3d)


    for i, vmap in enumerate(cspace_map):
        visibility_graph = Graph.visibility_graph(vmap)
        for v1 in visibility_graph.nodes:
            for v2 in v1.neighbors:
                ax.plot([v1.x,v2.x], [v1.y,v2.y], zs=i*INC, linewidth=1.0, c=colors.rgb2hex((1,0.1,0,0.9)))

    ax.set_xlim3d(-2, 16)
    ax.set_ylim3d(-2,10)
    ax.set_zlim3d(0,360)
    #ax.add_collection3d(Poly3DCollection(model))
    plt.show()

    # for angle in range(0, 360):
    #     ax.view_init(30, angle)
    #     plt.draw()
    #     plt.pause(.001)
