from shapely.geometry import Point, Polygon

class PlanPolygon(Polygon):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __add__(self, other):
        # minkowsky sum of two polygons
        newp = []
        for p1 in self.exterior.coords:
            for p2 in other.exterior.coords:
                x1,y1 = p1
                x2,y2 = p2
                newp.append((x1+x2, y1+y2))

        return MyPolygon(newp)

    def rotate(self, theta):
        newp = []
        for p in self.exterior.coords:
            x1, y1 = p
            newp.append((math.cos(theta)*x1 - math.sin(theta)*y1,
                math.sin(theta)*x1 + math.cos(theta)*y1))
        return MyPolygon(newp)
