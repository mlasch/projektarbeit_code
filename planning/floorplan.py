#!/usr/bin/env python3

import ezdxf
import numpy as np
import math

import matplotlib.pyplot as plt

from functools import reduce

def check_junction(p1, p2, p3, p4):

    x1, y1 = p1
    x2, y2 = p2
    x3, y3 = p3
    x4, y4 = p4

    a1 = y2 - y1
    b1 = x1 - x2
    c1 = a1 * x1 + b1 * y1
    a2 = y4 - y3
    b2 = x3 - x4
    c2 = a2 * x3 + b2 * y3

    den = a1*b2-a2*b1

    if den == 0:
        # division though zero, no intersection
        return False

    x = (b2*c1 - b1*c2)/ den
    y = (a1*c2 - a2*c1)/ den

    # dirty division by zero hack
    if (x2 - x1) == 0:
        rx0 = (x - x1) / (x2 - x1+0.001)
    else:
        rx0 = (x - x1) / (x2 - x1)

    if (y2 - y1) == 0:
        ry0 = (y - y1) / (y2 - y1+0.001)
    else:
        ry0 = (y - y1) / (y2 - y1)

    if (x4 - x3) == 0:
        rx1 = (x - x3) / (x4 - x3+0.001)
    else:
        rx1 = (x - x3) / (x4 - x3)

    if (y4 -y3) == 0:
        ry1 = (y - y3) / (y4 - y3+0.001)
    else:
        ry1 = (y - y3) / (y4 - y3)


    if ((rx0 > 0 and rx0 < 1) or (ry0 > 0 and ry0 < 1)) and ((rx1 > 0 and rx1 < 1) or (ry1 > 0 and ry1 < 1)):
        # intersection
        print("intersection")
        return True
    else:
        # no intersection
        print("no intersection")
        return False


    #plt.plot([x1,x2], [y1,y2])
    #plt.plot([x3,x4], [y3,y4])
    #plt.show()

class Edge(object):
    def __init__(self, start, end):
        self.start = start
        self.end = end

    def check_intersect(self, other):
        result =  check_junction(self.start, self.end, other.start, other.end)
        print("|-->Check: ",self, other)

        return result

    def __str__(self):
        return "<Edge {:1.1f},{:1.1f}-->{:1.1f},{:1.1f}>".format(self.start[0], self.start[1], self.end[0], self.end[1])

class Polygon(object):
    def __init__(self, vertexes=None):
        if vertexes == None:
            self.vertexes = []
        else:
            self.vertexes = vertexes

        self.edges = []

    def add_vertex(self, vertex):
        self.vertexes.append(vertex)

    def add_edge(self, edge):
        self.edges.append(edge)

    #def check_intersect(self, line):
    #    for edge in self.edges:
    #
    #        print("=======================")
    #        print("start", edge.start, edge.end)

    #        print("end", line.start, edge.end)
    #
    #        print("=======================")
    #        if edge.check_intersect(line):
    #            return True

    #    return False


class Floorplan(object):
    def __init__(self, dxf_path):
        self.polygons = []
        self.edges = []

        self.graph = []
        dwg = ezdxf.readfile(dxf_path)

        msp = dwg.modelspace()
        for polyline in msp.query('LWPOLYLINE'):
            polygon = Polygon()
            #print("Polygon:")

            #if polyline[0] == polyline[-1]:
            #    del polyline[-1]

            last_point = None
            for point in polyline:
                x, y, start_width, end_width, bulge = point

                #print(x,y)
                polygon.add_vertex((x,y))

                if last_point != None:
                    edge = Edge(last_point, (x,y))
                    polygon.add_edge(edge)

                last_point = (x,y)

            self.polygons.append(polygon)

    def get_obstacles(self):
        for polygon in self.polygons:
            yield polygon.vertexes

    def get_cspace(self):
        pass

    def generate_graph(self,screen):
        """
        Generate a graph, connecting all vertexes which can be
        reachted directly.
        """

        for polygon in self.polygons:
            # add polygon edges to graph
            for edge in polygon.edges:
                self.graph.append(edge)

            # find edges between polygons
            for vertex in polygon.vertexes:
                for polygon_search in self.polygons:
                    if polygon_search == polygon:
                        # no edges within a polygon
                        continue

                    for vertex_search in polygon_search.vertexes:
                        line = Edge(vertex, vertex_search)

                        print("====> check nex line in graph: ", line)

                        # check weather line intersects with any polygon edge

                        for polygon_intersect in self.polygons:
                            print("Check polygon intersection:")
                            append = True
                            for edge in polygon_intersect.edges:
                                #print("CHECK EDGE", edge)

                                # result=True -> intersection found
                                intersect = line.check_intersect(edge)
                                yield line, edge, intersect

                                if intersect:
                                    break

                            if intersect:
                                print("found intersection")
                                append = False
                                break



                        if append:
                            self.graph.append(line)

                            #if polygon_intersect.check_intersect(line):
                            #    print("interrupt ")
                            #    intersect = True
                            #    break

                        #if intersect:
                        #    #graph.append(line)
                        #    yield(line, False)
                        #else:
                        #    yield(line, True


    def set_width(self, width, margin=100):
        """
        Transform dxf coordinates to pygame coordinates.
        """

        #print(self.polygons[0].vertexes)
        #all_vertexes = reduce(lambda p1,p2: p1.vertexes + p2.vertexes, self.polygons)
        for polygon in self.polygons:
            for i, vertex in enumerate(polygon.vertexes):
                x, y = vertex
                polygon.vertexes[i] = (x,-1*y)

        for polygon in self.polygons:
            for i, edge in enumerate(polygon.edges):
                x,y = edge.start
                polygon.edges[i].start = (x,-1*y)
                x,y = edge.end
                polygon.edges[i].end = (x,-1*y)

        all_vertexes = []
        for polygon in self.polygons:
            all_vertexes += polygon.vertexes

        all_x, all_y = zip(*all_vertexes)

        #all_y = list(filter(lambda x:x*-1, all_y))
        #print("ALL Y ",all_y)

        xmin = min(all_x)-margin;
        xmax = max(all_x)+margin;
        ymin = min(all_y)-margin; 
        ymax = max(all_y)+margin

        self.scale = width/(xmax-xmin)
        self.xoffset = xmin

        height = (ymax-ymin)*self.scale

        #print("height", height)
        #yscale = height/(ymax-ymin)
        self.yoffset = ymin

        #print(f"scale: {scale}")
        print("BOUNARIES", xmin, xmax, ymin, ymax)

        #for polygon in self.polygons:
        #    for i, vertex in enumerate(polygon.vertexes):
        #        x, y = vertex
        #        x -= xoffset
        #        x *= scale
        #        y -= yoffset
        #        y *= scale
        #        polygon.vertexes[i] = (x,y)
        #        print("VERTEX after rescale: {},{}".format(x,y))

        #    for edge in polygon.edges:
        #        print("EDGE before rescale: {}".format(edge))
        #        x, y = edge.start
        #        x -= xoffset
        #        x *= scale
        #        y -= yoffset
        #        y *= scale
        #        edge.start = (x,y)
        #
        #
        #        x, y = edge.end
        #        x -= xoffset
        #        x *= scale
        #        y -= yoffset
        #        y *= scale
        #        edge.end = (x,y)
        #
        #        print("EDGE after rescale: {}".format(edge))

        #for polygon in self.polygons:
        #    #print("Polygon:")
        #
        #    old = None
        #    for vertex in polygon.vertexes:
        #        if old != None:
        #            x1,y1 = old
        #            x2,y2 = vertex

        #            distance = math.sqrt(math.pow(x2-x1,2) + math.pow(y2-y1,2))
        #            #print(distance, end='-> ')
        #        old = vertex
        #    #print()

        #    #print(polygon.vertexes)

        print(f"SCREEN SIZE: {width}, {height}")

        return width, height

    def scale_xy(self, x, y):
        x -= self.xoffset
        x *= self.scale
        y -= self.yoffset
        y *= self.scale

        return x,y
