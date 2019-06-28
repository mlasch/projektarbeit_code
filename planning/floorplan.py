#!/usr/bin/env python3

import ezdxf
import numpy as np
import math

import matplotlib.pyplot as plt

from functools import reduce
from collections import OrderedDict
from time import time

from planning.shapes import Point, PlanPolygon, LineString
from shapely.ops import polygonize_full, unary_union
import networkx as nx
from networkx import astar_path
from networkx.exception import NodeNotFound, NetworkXError


class Vertex:
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        #self.p = Point(x,y)

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __hash__(self):
        return hash((self.x, self.y))


    def __repr__(self):
        return "{} {}".format(self.x, self.y)

    def weight(self, other):
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5


class Floorplan(object):
    def __init__(self, dxf_path, position=None):
        self.dxf_path = dxf_path
        self.world_xoffset = 2159
        self.world_yoffset = 7781

        INC = 5
        self.obstacles = []
        self.bobstacles = []

        self.old_start = None
        self.old_dest = None

        self.angles = np.linspace(0,2*np.pi, INC)
        self.angles = np.append(self.angles[:-1], [0])
        print(self.angles)
        #self.robot = PlanPolygon([(-140, -650), (140,-650), (350,-500), (350,500), (225,800), (-225,800), (-350,500), (-350,-500)]);
        self.robot = PlanPolygon([(-140, -650), (140,-650), (350,-500), (350,500), \
         (225,800), (-225,800), (-350,500), (-350,-500)]).rotate(-math.pi/2);
        self.cspaces = [[] for _ in range(len(self.angles))]
        self.lines = [[] for _ in range(len(self.angles))]
        self.vertical = [[] for _ in range(len(self.angles))]

        self.graph = None


        if position == None:
            self.position = ({'x':-62, 'y':942}, 0)
        else:
            self.position = position

        self.load_map()


    def load_map(self):
        dwg = ezdxf.readfile(self.dxf_path)

        self.obstacles = []
        self.cspaces = [[] for _ in range(len(self.angles))]

        msp = dwg.modelspace()
        for polyline in msp.query('LWPOLYLINE'):
            polygon = []

            for point in polyline:
                xc, yc, start_width, end_width, bulge = point

                # turn axes and
                # set offset to match world coordinates
                xw = yc - self.world_xoffset
                yw = -(xc - self.world_yoffset)

                polygon.append((xw, yw))

            self.obstacles.append(PlanPolygon(polygon))

        robot_radius = self.get_robot_buffer()

        self.bobstacles = []

        for obstacle in self.obstacles:
            self.bobstacles.append(obstacle.buffer(robot_radius/2).simplify(20))
            #self.bobstacles.append(obstacle)

        ###### DEBUG
        # for obstacle in self.bobstacles:
        #     plt.plot(*obstacle.exterior.coords.xy)
        # plt.axis('equal')
        # plt.show()
        ###### END DEBUG

        # preload graph
        print("Start preloading graph")
        tstart = time()
        self.graph = nx.Graph()
        print("{} {}".format(len(self.graph.nodes()), len(self.graph.edges())))
        for obstacle1 in self.bobstacles:
            for v1 in obstacle1.exterior.coords:
                for obstacle2 in self.bobstacles:
                    for v2 in obstacle2.exterior.coords:
                        if v1 == v2:
                            # same vertices
                            continue

                        line = LineString([v1, v2])

                        is_sightline = True
                        # union_bobstacles = unary_union(self.bobstacles)
                        # if line.within(union_bobstacles) or line.crosses(union_bobstacles):
                        #     is_sightline = False

                        for obstacle3 in self.bobstacles:
                            if line.within(obstacle3) or line.crosses(obstacle3):
                                is_sightline = False

                        if is_sightline:
                            vx1 = Vertex(*v1)
                            vx2 = Vertex(*v2)
                            self.graph.add_edge(vx1, vx2, weight=vx1.weight(vx2))

        tend = time()
        print("Preloaded graph in {} with {} nodes and {} edges".format(tend-tstart,
        len(self.graph.nodes()),
        len(self.graph.edges())))

    def update_sight_graph(self, start, dest):

        if self.old_start and self.old_dest:
            self.graph.remove_node(self.old_start)
            self.graph.remove_node(self.old_dest)

        for obstacle1 in self.bobstacles:
            for v1 in obstacle1.exterior.coords:
                for v2 in [(start.x, start.y), (dest.x, dest.y)]:
                    line = LineString([v1, v2])

                    is_sightline = True
                    tstart1 = time()
                    #union_bobstacles = unary_union(self.bobstacles)
                    #print("union:", time()-tstart1)

                    for obstacle3 in self.bobstacles:
                        if line.within(obstacle3) or line.crosses(obstacle3):
                            is_sightline = False

                    if is_sightline:
                        vx1 = Vertex(*v1)
                        vx2 = Vertex(*v2)
                        self.graph.add_edge(vx1, vx2, weight=vx1.weight(vx2))


        #### DEBUG plotting
        # ## OBSTACLES
        # for obstacle in self.bobstacles:
        #     plt.fill(*obstacle.exterior.coords.xy)
        #
        #
        # ## Graph
        # for edge in self.graph.edges():
        #     v1, v2 = edge
        #     plt.plot([v1.x, v2.x], [v1.y, v2.y], lineWidth=1, color='k')
        #
        # for node in self.graph.nodes():
        #     plt.scatter(node.x, node.y, s=10, color='b')
        #
        # ## Path
        #
        # plt.axis('equal')
        # plt.show()
        #### END DEBUG plotting

    def get_obstacles(self):
        for polygon in self.obstacles:
            yield list(polygon.exterior.coords)

    def update_pos(self, position):
        self.position = position

    def get_robot_buffer(self):
        """
        Computes the minimum circle radius around the robot
        """
        max_dist = 0
        for line in self.robot.exterior.coords:
            cur_dist = Point(0,0).distance(Point(*line))
            if max_dist < cur_dist:
                max_dist = cur_dist
        return max_dist

    def shortest_path(self, vstart, vdest):
        try:
            path = nx.astar_path(self.graph, vstart, vdest)
            self.old_start = vstart
            self.old_dest = vdest

        except NodeNotFound as nf:
            print("Node not found, {}".format(nf))
            self.old_start = None
            self.old_dest = None
            path = [] # return empty list

        return path

    def path_planner(self, destination):
        vdest = Vertex(*destination)
        vstart = Vertex(self.position[0]['x'], self.position[0]['y'])

        print(vstart, "->" ,vdest)

        self.update_sight_graph(vstart, vdest)

        path = self.shortest_path(vstart, vdest)

        checkpoints = []
        for p in path:
            checkpoints.append((p.x, p.y))

        return checkpoints
