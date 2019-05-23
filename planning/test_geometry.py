#!/usr/bin/env python3

import unittest

from cspace_3d import Vertex, Edge, Obstacle, Graph

class TestVisibilityGraph(unittest.TestCase):
    def setUp(self):
        self.o1 = Obstacle([Vertex(7,-4), Vertex(8,-7), Vertex(10,-4), Vertex(10,4), Vertex(7,4)])

        self.o2 = Obstacle([Vertex(0,0), Vertex(4,-5), Vertex(2,4)])
        self.o3 = Obstacle([Vertex(7,-1), Vertex(9,-1), Vertex(9,6), Vertex(7,6)])
        self.o4 = Obstacle([Vertex(11,-3), Vertex(13,1), Vertex(11,-3)])
        self.map1 = [self.o2, self.o3]

    def test_lineintersect(self):
        # intersect
        a = Edge(Vertex(0,0), Vertex(1,1))
        b = Edge(Vertex(0,1), Vertex(1,0))
        self.assertTrue(a.intersect(b) != False)
        self.assertTrue(b.intersect(a) != False)
        # parallel
        a = Edge(Vertex(0,0), Vertex(1,1))
        b = Edge(Vertex(0,1), Vertex(1,2))
        self.assertFalse(a.intersect(b))
        self.assertFalse(b.intersect(a))
        # colinear *TODO*
        # a = Edge(Vertex(1.1,1.1), Vertex(2.2,2.2))
        # b = Edge(Vertex(1.2,1.2), Vertex(1.3,1.3))
        # self.assertTrue(a.intersect(b) != False)
        # self.assertTrue(b.intersect(a) != False)

    def test_sight_line(self):
        self.assertFalse(self.o1.check_line(Edge(Vertex(0,0), Vertex(11,0))))
        self.assertTrue(self.o1.check_line(Edge(Vertex(0,0), Vertex(6,0))))
        self.assertTrue(self.o1.check_line(Edge(Vertex(2,-13), Vertex(25,-2))))

    def test_sight_graph(self):
        graph = Graph.visibility_graph(self.map1)

        self.assertEqual(len(graph), 7)

    def test_cspace(self):
        self.assertTrue(False)

if __name__ == '__main__':
    unittest.main()
