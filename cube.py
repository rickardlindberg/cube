"""
                   y
                   ^   z
                   |  ^
                   | /
                   |/
                   O------> x

>>> Body.unit().extend_z().extend_y().extend_x().print()
y     z     y
|11   |21   | 2
|2    |1    |11
+--x  +--x  +--z

>>> Body.unit().extend_x().back().extend_y().back().extend_z().print()
y     z     y
|1    |1    |1
|21   |21   |21
+--x  +--x  +--z
"""

import collections

class Body:

    @classmethod
    def unit(cls):
        return Body(points=Points([Point3D.origin()]))

    def __init__(self, points):
        self.points = points

    def extend_x(self):
        return self.extend(dx=1)

    def extend_y(self):
        return self.extend(dy=1)

    def extend_z(self):
        return self.extend(dz=1)

    def back(self):
        return Body(self.points.swap_last())

    def extend(self, **kwargs):
        return Body(self.points.extend(**kwargs).normalize())

    def print(self):
        grid = Grid()
        origin = Point2D(x=0, y=0)
        for horizontal_axis_name, vertical_axis_name, fn in [
            ("x", "y", lambda point: point.xy()),
            ("x", "z", lambda point: point.xz()),
            ("z", "y", lambda point: point.zy()),
        ]:
            plane_points = self.points.filter(fn)
            max_plane_point = plane_points.bounding_max()
            grid.add(origin, "+")
            for vertical in max_plane_point.rows():
                vertical = vertical.set(x=0).add(origin).move(dy=1)
                grid.add(vertical, "|")
            grid.add(vertical.move(dy=1), vertical_axis_name)
            for horizontal in max_plane_point.columns():
                horizontal = horizontal.set(y=0).add(origin).move(dx=1)
                grid.add(horizontal, "-")
            grid.add(horizontal.move(dx=1), horizontal_axis_name)
            for point in plane_points:
                count = plane_points.count(point)
                assert 1 <= count <= 9
                grid.add(point.add(origin).move(dx=1, dy=1), str(count))
            origin = origin.move(dx=max_plane_point.x+5)
        grid.print()

class Points:

    def __init__(self, points):
        self.points = list(points)

    def __iter__(self):
        return iter(list(self.points))

    def count(self, point):
        return len([x for x in self.points if x == point])

    def swap_last(self):
        return Points(self.points[:-2]+self.points[-2:][::-1])

    def filter(self, fn):
        return Points([
            fn(point) for point in self.points
        ]).normalize()

    def normalize(self):
        delta = self.bounding_min().multiply(-1)
        return Points([
            point.add(delta)
            for point in self.points
        ])

    def bounding_min(self):
        min_point = None
        for point in self.points:
            if min_point is None:
                min_point = point
            else:
                min_point = min_point.bounding_min(point)
        return min_point

    def bounding_max(self):
        max_point = None
        for point in self.points:
            if max_point is None:
                max_point = point
            else:
                max_point = max_point.bounding_max(point)
        return max_point

    def add(self, point):
        return Points(self.points+[point])

    def extend(self, **kwargs):
        return self.add(self.points[-1].move(**kwargs))

class Point3D(collections.namedtuple("Point3D", ["x", "y", "z"])):

    @classmethod
    def origin(cls):
        return cls(x=0, y=0, z=0)

    def bounding_min(self, other):
        return Point3D(
            x=min(self.x, other.x),
            y=min(self.y, other.y),
            z=min(self.z, other.z),
        )

    def add(self, other):
        return self.move(dx=other.x, dy=other.y, dz=other.z)

    def multiply(self, factor):
        return Point3D(
            x=factor*self.x,
            y=factor*self.y,
            z=factor*self.z,
        )

    def xy(self):
        return Point2D(x=self.x, y=self.y)

    def xz(self):
        return Point2D(x=self.x, y=self.z)

    def zy(self):
        return Point2D(x=self.z, y=self.y)

    def move(self, dx=0, dy=0, dz=0):
        return Point3D(x=self.x+dx, y=self.y+dy, z=self.z+dz)

class Point2D(collections.namedtuple("Point2D", ["x", "y"])):

    def bounding_min(self, other):
        return Point2D(x=min(self.x, other.x), y=min(self.y, other.y))

    def bounding_max(self, other):
        return Point2D(x=max(self.x, other.x), y=max(self.y, other.y))

    def set(self, **kwargs):
        return self._replace(**kwargs)

    def multiply(self, factor):
        return Point2D(x=factor*self.x, y=factor*self.y)

    def add(self, other):
        return self.move(dx=other.x, dy=other.y)

    def move(self, dx=0, dy=0):
        return self._replace(x=self.x+dx, y=self.y+dy)

    def rows(self):
        for y in range(self.y+1):
            yield self._replace(y=y)

    def columns(self):
        for x in range(self.x+1):
            yield self._replace(x=x)

class Grid:

    def __init__(self):
        self.values = {}

    def add(self, point, char):
        self.values[point] = char

    def print(self):
        points = Points(self.values)
        for row_point in reversed(list(points.bounding_max().rows())):
            line = []
            for column_point in row_point.columns():
                line.append(self.values.get(column_point, " "))
            print("".join(line).rstrip())

if __name__ == "__main__":
    import doctest
    doctest.testmod()
    print("OK")
