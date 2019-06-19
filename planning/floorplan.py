#!/usr/bin/env python3

import ezdxf
import numpy as np
import math

import matplotlib.pyplot as plt

from functools import reduce
from collections import OrderedDict

from planning.shapes import Point, PlanPolygon, LineString
from shapely.ops import polygonize_full, cascaded_union, unary_union
import networkx as nx
from networkx import astar_path

# class Edge(object):
#     def __init__(self, start, end):
#         self.start = start
#         self.end = end
#
#     def check_intersect(self, other):
#         result =  check_junction(self.start, self.end, other.start, other.end)
#         print("|-->Check: ",self, other)
#
#         return result
#
#     def __str__(self):
#         return "<Edge {:1.1f},{:1.1f}-->{:1.1f},{:1.1f}>".format(self.start[0], self.start[1], self.end[0], self.end[1])

# class Polygon(object):
#     def __init__(self, vertexes=None):
#         if vertexes == None:
#             self.vertexes = []
#         else:
#             self.vertexes = vertexes
#
#         self.edges = []
#
#     def add_vertex(self, vertex):
#         self.vertexes.append(vertex)
#
#     def add_edge(self, edge):
#         self.edges.append(edge)
#
#     #def check_intersect(self, line):
#     #    for edge in self.edges:
#     #
#     #        print("=======================")
#     #        print("start", edge.start, edge.end)
#
#     #        print("end", line.start, edge.end)
#     #
#     #        print("=======================")
#     #        if edge.check_intersect(line):
#     #            return True
#
#     #    return False

class Vertex:
    def __init__(self, point, theta, parent=None, neighbors=None):
        self.point = point
        self.theta = theta

        if not parent:
            self.parent = []
        else:
            self.parent = parent

        if not neighbors:
            self.neighbors = []
        else:
            self.neighbors = neighbors

HYPOTENUSE = 10000

class Floorplan(object):
    def __init__(self, dxf_path, position=None):
        self.dxf_path = dxf_path
        self.world_xoffset = 2159
        self.world_yoffset = 7781

        INC = 5
        self.obstacles = []
        self.angles = np.linspace(0,2*np.pi, INC)
        self.angles = np.append(self.angles[:-1], [0])
        print(self.angles)
        #self.robot = PlanPolygon([(-140, -650), (140,-650), (350,-500), (350,500), (225,800), (-225,800), (-350,500), (-350,-500)]);
        self.robot = PlanPolygon([(-140, -650), (140,-650), (350,-500), (350,500), \
         (225,800), (-225,800), (-350,500), (-350,-500)]).rotate(-math.pi/2);
        self.cspaces = [[] for _ in range(len(self.angles))]
        self.lines = [[] for _ in range(len(self.angles))]
        self.vertical = [[] for _ in range(len(self.angles))]

        self.graph = nx.Graph()


        if position == None:
            self.position = ({'x':0, 'y':0}, 0)
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

                polygon.append((xw,yw))

            self.obstacles.append(PlanPolygon(polygon))

        #self.preload_cspace()

    def preload_cspace(self):
        print("PRELOAD CSPACE")
        # preload cspace
        for theta_idx, theta in enumerate(self.angles):
            for obstacle in self.obstacles:
                cspace = (self.robot.rotate(theta)+obstacle).convex_hull
                self.cspaces[theta_idx].append(cspace)

        # create lines, TODO: cut lines a max coordinates of map
        for theta_idx, theta in enumerate(self.angles):
            # Line Collection
            for cspace in self.cspaces[theta_idx]:

                #### Add directional lines to the line collection
                for vertex in cspace.exterior.coords:
                    x0, y0 = vertex

                    x1 = x0 + HYPOTENUSE*np.cos(theta)
                    y1 = y0 + HYPOTENUSE*np.sin(theta)
                    x2 = x0 - HYPOTENUSE*np.cos(theta)
                    y2 = y0 - HYPOTENUSE*np.sin(theta)

                    line1 = LineString([(x0,y0), (x2,y2)])
                    line2 = LineString([(x1,y1), (x0,y0)])
                    fragments = [line1, line2]

                    for cspace_check in self.cspaces[theta_idx]:
                        fragments_temp = []
                        for cline in fragments:
                            fragment = cline.difference(cspace_check.buffer(-0.001)) # HACK
                            #fragment = cline.difference(cspace_check)
                            try:
                                fragments_temp.extend(fragment)
                            except TypeError:
                                fragments_temp.append(fragment)
                        fragments = fragments_temp

                    self.lines[theta_idx].extend(fragments)

            print(len(self.lines[theta_idx]))


        # for theta in [0, 0.1*math.pi]:
        #     if theta not in self.cspace.keys():
        #         self.cspace.update({theta: []})
        #
        #     for polygon in self.polygons:
        #         p1 = self.robot.rotate(theta)+polygon
        #
        #         # remove vetexes along a line
        #         result, dangles, cuts, invalids = polygonize_full(p1.convex_hull.exterior)
        #
        #         if len(result) > 1:
        #             raise TypeError
        #         self.cspace[theta].append(result[0]) # use first result from function
        #
        #     polygons = unary_union(self.cspace[theta])
        #     #self.cspace[theta] = polygons
        #     #print(polygons.interior)
        #
        # # create navigation graph
        # self.create_graph()


        ################################# plotting

        for line in self.lines[0]:
            plt.plot(*line.coords.xy)

        # for polygon in self.polygons:
        #     plt.scatter(*polygon.exterior.coords.xy)
        # theta = 0.1*math.pi
        # plt.plot(*self.robot.rotate(theta).exterior.coords.xy, linewidth=2)
        #
        for polygon in self.cspaces[0]:
            #plt.scatter(*polygon.exterior.coords.xy)
            plt.plot(*polygon.exterior.coords.xy, linewidth='2', color='k')

        plt.show()
        #
        # for p1 in self.cspace[theta]:
        #     for p2 in self.cspace[theta]:
        #         if p1 == p2:
        #             continue
        #
        #         pint = p1.exterior.intersection(p2.exterior)
        #         for p in pint:
        #             plt.scatter(*p.coords.xy, marker='x')
        #
        # for line in self.graph[theta]:
        #     plt.plot(*line.coords.xy, linewidth=0.4, color='black')
        #
        # plt.show()

        #############################################3


    def get_obstacles(self):
        for polygon in self.obstacles:
            yield list(polygon.exterior.coords)

    def update_pos(self, position):
        self.position = position

    def update_graph(self):
        pass





        # # generate sight graph
        # theta = 0.1*math.pi
        # if theta not in self.graph.keys():
        #     self.graph.update({theta: []})
        #     #self.graph = nx.Graph()
        #
        # vertexes = []
        # for p1 in self.cspace[theta]:
        #     for x1, y1 in p1.exterior.coords:
        #         point1 = Point(x1,y1)
        #         v = Vertex(point1, theta, parent=p1)
        #         is_within = False
        #         for polygon_check in self.cspace[theta]:
        #             if point1.within(polygon_check):
        #                 is_within = True
        #         if not is_within:
        #             vertexes.append(v)
        #
        #     # add vertexes on polygon intersections
        #     for p2 in self.cspace[theta]:
        #         if p1 == p2:
        #             continue
        #
        #         pint = p1.exterior.intersection(p2.exterior)
        #         for p in pint:
        #             for x2,y2 in p.coords:
        #                 v = Vertex(Point(x2, y2),theta, parent=p1)
        #                 vertexes.append(v)
        #
        # for v1 in vertexes:
        #     for v2 in vertexes:
        #         if v1 == v2:
        #             continue
        #
        #         line = LineString([v1.point, v2.point])
        #         append = True
        #         for polygon in self.cspace[theta]:
        #             intersect = line.crosses(polygon) or line.within(polygon)
        #             # print(polygon)
        #             # print(line)
        #             # print(intersect)
        #             # plt.plot(*polygon.exterior.coords.xy)
        #             # plt.plot(*line.coords.xy)
        #             # plt.show()
        #
        #             if intersect:
        #                 append = False
        #                 break
        #
        #         if append:
        #             #self.graph.add_edge(v1, v2)
        #             self.graph[theta].append(line)


    def shortest_path(self, destination):
        xd, yd = destination
        checkpoints = [(xd, yd, 0), (8721, 900, 0), (0)]

        return checkpoints

    def path_planner(self, destination):
        xd, yd = destination

        checkpoints = self.shortest_path(destination)

        return checkpoints


    # def generate_graph(self,screen):
    #     """
    #     Generate a graph, connecting all vertexes which can be
    #     reachted directly.
    #     """
    #
    #     for polygon in self.polygons:
    #         # add polygon edges to graph
    #         for edge in polygon.edges:
    #             self.graph.append(edge)
    #
    #         # find edges between polygons
    #         for vertex in polygon.vertexes:
    #             for polygon_search in self.polygons:
    #                 if polygon_search == polygon:
    #                     # no edges within a polygon
    #                     continue
    #
    #                 for vertex_search in polygon_search.vertexes:
    #                     line = Edge(vertex, vertex_search)
    #
    #                     print("====> check nex line in graph: ", line)
    #
    #                     # check weather line intersects with any polygon edge
    #
    #                     for polygon_intersect in self.polygons:
    #                         print("Check polygon intersection:")
    #                         append = True
    #                         for edge in polygon_intersect.edges:
    #                             #print("CHECK EDGE", edge)
    #
    #                             # result=True -> intersection found
    #                             intersect = line.check_intersect(edge)
    #                             yield line, edge, intersect
    #
    #                             if intersect:
    #                                 break
    #
    #                         if intersect:
    #                             print("found intersection")
    #                             append = False
    #                             break
    #
    #
    #
    #                     if append:
    #                         self.graph.append(line)
    #
    #                         #if polygon_intersect.check_intersect(line):
    #                         #    print("interrupt ")
    #                         #    intersect = True
    #                         #    break
    #
    #                     #if intersect:
    #                     #    #graph.append(line)
    #                     #    yield(line, False)
    #                     #else:
    #                     #    yield(line, True


    # def set_width(self, width, margin=100):
    #     """
    #     Transform dxf coordinates to pygame coordinates.
    #     """
    #
    #     #print(self.polygons[0].vertexes)
    #     #all_vertexes = reduce(lambda p1,p2: p1.vertexes + p2.vertexes, self.polygons)
    #     for polygon in self.polygons:
    #         for i, vertex in enumerate(polygon.vertexes):
    #             x, y = vertex
    #             polygon.vertexes[i] = (x,-1*y)
    #
    #     for polygon in self.polygons:
    #         for i, edge in enumerate(polygon.edges):
    #             x,y = edge.start
    #             polygon.edges[i].start = (x,-1*y)
    #             x,y = edge.end
    #             polygon.edges[i].end = (x,-1*y)
    #
    #     all_vertexes = []
    #     for polygon in self.polygons:
    #         all_vertexes += polygon.vertexes
    #
    #     all_x, all_y = zip(*all_vertexes)
    #
    #     #all_y = list(filter(lambda x:x*-1, all_y))
    #     #print("ALL Y ",all_y)
    #
    #     xmin = min(all_x)-margin;
    #     xmax = max(all_x)+margin;
    #     ymin = min(all_y)-margin;
    #     ymax = max(all_y)+margin
    #
    #     self.scale = width/(xmax-xmin)
    #     self.xoffset = xmin
    #
    #     height = (ymax-ymin)*self.scale
    #
    #     #print("height", height)
    #     #yscale = height/(ymax-ymin)
    #     self.yoffset = ymin
    #
    #     print("BOUNARIES", xmin, xmax, ymin, ymax)
    #
    #     return width, height
    #
    # def scale_xy(self, x, y):
    #     x -= self.xoffset
    #     x *= self.scale
    #     y -= self.yoffset
    #     y *= self.scale
    #
    #     return x,y
