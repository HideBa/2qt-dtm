# -- my_code_hw01.py
# -- geo1015.2023.hw01
# -- Hidemichi Baba
# -- 5967538

import startinpy
import numpy as np
import time
import math

"""
You can add any new function to this unit.

Do not modify the functions given or change the signature of the functions.

You can use any packages from the Python standard Library
(therefore nothing with pip install, except those allowed for hw01).

You need to complete the 3 functions below:
  1. `get_voronoi_edges()`
  1. `get_area_voronoi_cell()`
  1. `interpolate_tin()`

"""


class Tin:
    def __init__(self):
        self.dt = startinpy.DT()

    def number_of_vertices(self):
        return self.dt.number_of_vertices()

    def number_of_triangles(self):
        return self.dt.number_of_triangles()

    def insert_one_pt(self, x, y, z):
        self.dt.insert_one_pt(x, y, z)

    def info(self):
        print(self.dt.points)

    def get_delaunay_vertices(self):
        return self.dt.points

    def get_delaunay_edges(self):
        pts = self.dt.points
        edges = []
        for tr in self.dt.triangles:
            a = pts[tr[0]]
            b = pts[tr[1]]
            c = pts[tr[2]]
            edges.append(a)
            edges.append(b)
            edges.append(a)
            edges.append(c)
            edges.append(b)
            edges.append(c)
        return edges

    def get_voronoi_edges(self):
        """
        Function that returns all the Voronoi edges of the bounded
        Voronoi cells in the dataset.

        Input:
            none
        Output:
            edges: an array of points (a point is an array with 2 values [x, y]).
                   each consecutive pair forms an edge.
                   if edges = [ [0., 0.], [1., 0.], [1., 1.], [0., 1.] ] then 2 edges
                   will be drawn: (0,0)->(1,0) + (1,1)->(0,1)
                   (function get_delaunay_edges() uses the same principle)
        """
        edges = []
        triangles = self.dt.triangles
        visited_triangles = []
        for tri in triangles:
            adjacent_triangles = self.dt.adjacent_triangles_to_triangle(tri)
            for a_tri in adjacent_triangles:
                if a_tri in visited_triangles:
                    continue
                a1 = self.dt.points[a_tri[0]]
                b1 = self.dt.points[a_tri[1]]
                c1 = self.dt.points[a_tri[2]]
                cc1 = self.circumcircle_center(a1, b1, c1)
                a2 = self.dt.points[tri[0]]
                b2 = self.dt.points[tri[1]]
                c2 = self.dt.points[tri[2]]
                cc2 = self.circumcircle_center(a2, b2, c2)
                if cc1 is None or cc2 is None:
                    continue
                if not (self.dt.is_finite(tri) and self.dt.is_finite(a_tri)):
                    continue  # If a triangle is infinit, it doesn't need to draw
                edge = [cc1, cc2]
                edges.append(edge)
            # TODO: add convex hull edges
        np_edges = np.array(edges)
        unique_edges = np.unique(np_edges, axis=0)
        edges_list = unique_edges.tolist()
        flatten_edges = [item for sublist in edges_list for item in sublist]
        return flatten_edges

    # Ref: https://github.com/hugoledoux/startin/blob/574e3c8cd06aa5b03b86f867b1fb69f21c0f81c5/src/interpolation/mod.rs#L174C1-L174C5
    def interpolate_tin(self, x, y):
        """
        !!! TO BE COMPLETED !!!

        Function that interpolates linearly in a TIN.

        Input:
            x:      x-coordinate of the interpolation location
            y:      y-coordinate of the interpolation location
        Output:
            z: the estimation of the height value,
               numpy.nan if outside the convex hull
               (NaN: Not a Number https://numpy.org/devdocs/reference/constants.html#numpy.nan)
        """
        q = (x, y)
        # if not is_inside_convex_hull(q, convex_hull(self.dt.points)):
        #     raise ValueError("Point is outside the convex hull")
        # TODO: check if it allowed or not
        if not self.dt.is_inside_convex_hull(x, y):
            return np.nan
            # raise ValueError("Point is outside the convex hull")

        # closest 3 points TODO: check later here
        sorted_points = self.closer_point((x, y))
        p0, p1, p2 = sorted_points[0], sorted_points[1], sorted_points[2]
        xyp1, xyp2, xyp3 = (p0[0], p0[1]), (p1[0], p1[1]), (p2[0], p2[1])
        a0 = area_triangle(q, xyp2, xyp3)
        a1 = area_triangle(q, xyp1, xyp3)
        a2 = area_triangle(q, xyp1, xyp2)
        total = 0.0
        total += p0[2] * a0
        total += p1[2] * a1
        total += p2[2] * a2
        result = total / (a0 + a1 + a2)
        print("result", result)
        print("other z values", p0[2], p1[2], p2[2])
        return result

    # Ref: https://github.com/hugoledoux/startin/blob/574e3c8cd06aa5b03b86f867b1fb69f21c0f81c5/src/lib.rs#L1478
    def get_area_voronoi_cell(self, vi):
        """
        !!! TO BE COMPLETED !!!

        Function that obtain the area of one Voronoi cells.

        Input:
            vi:     the position of the vertex in the TIN structure to display
        Output:
            z: the area of vi Voronoi cell,
               return numpy.inf if the cell is unbounded
               (infinity https://numpy.org/devdocs/reference/constants.html#numpy.inf)
        """
        # print(vi)
        # print("points---", self.dt.points)
        # try:
        #     adjacent_vertecies = self.dt.adjacent_vertices_to_vertex(vi)
        # except Exception as e:
        #     print("vi is not in the TIN", e)
        #     return np.inf
        # centers = []

        # for i, adj_v in enumerate(adjacent_vertecies):
        #     # Ref:https://github.com/hugoledoux/startin/blob/574e3c8cd06aa5b03b86f867b1fb69f21c0f81c5/src/lib.rs#L225
        #     j = i + 1  # TODO: fix later
        #     circle_center = self.circumcircle_center(
        #         self.dt.points[vi],
        #         self.dt.points[adj_v],
        #         self.dt.points[j],
        #     )
        #     centers.append(circle_center)
        # total_area = 0.0
        # for i in range(0, len(centers), 2):
        #     if centers[i] is None or centers[i + 1]:
        #         continue
        #     total_area += area_triangle(self.dt.points[vi], centers[i], centers[i + 1])
        # return total_area
        return np.Infinity

    # TODO: change to implement this ref: https://github.com/hugoledoux/startin/blob/574e3c8cd06aa5b03b86f867b1fb69f21c0f81c5/src/geom/mod.rs#L18C3-L18C3
    def circumcircle_center(self, p1, p2, p3):
        ax, ay = p1[0], p1[1]
        bx, by = p2[0], p2[1]
        cx, cy = p3[0], p3[1]
        d = 2.0 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by))
        if d == 0:
            return None
        ux = (
            (ax**2 + ay**2) * (by - cy)
            + (bx**2 + by**2) * (cy - ay)
            + (cx**2 + cy**2) * (ay - by)
        ) / d
        uy = (
            (ax**2 + ay**2) * (cx - bx)
            + (bx**2 + by**2) * (ax - cx)
            + (cx**2 + cy**2) * (bx - ax)
        ) / d
        # radius = math.dist((ux, uy), (ax, ay))
        return [ux, uy]

    def closer_point(self, point):
        """
        The function returns sorted points by distance from the given point.
        Input:
            point:     the position of vertex
        Output:
            sorted_points: sorted points by distance from the given point
        """
        points = self.dt.points
        sorted_points = sorted(
            points, key=lambda p: math.dist((p[0], p[1]), point)
        )  # Memo: Python's sorted method doesn't change original list
        return sorted_points


# Ref: https://github.com/hugoledoux/startin/blob/574e3c8cd06aa5b03b86f867b1fb69f21c0f81c5/src/geom/mod.rs#L14
def area_triangle(a, b, c):
    return det3x3t(a, b, c) / 2.0


# Ref: https://github.com/hugoledoux/startin/blob/574e3c8cd06aa5b03b86f867b1fb69f21c0f81c5/src/geom/mod.rs#L10
def det3x3t(a, b, c):
    return ((a[0] - c[0]) * (b[1] - c[1])) - ((a[1] - c[1]) * (b[0] - c[0]))


def orientation(p, q, r):
    """Calculate the orientation of the triplet (p, q, r).
    Returns positive if counter-clockwise, negative if clockwise, zero if collinear."""
    return (q[1] - p[1]) * (r[0] - q[0]) - (q[0] - p[0]) * (r[1] - q[1])


def convex_hull(points):
    if len(points) <= 3:
        # TODO: check later
        return points
    start = min(points, key=lambda p: (p[1], p[0]))

    # Sort points by polar angle with start
    def polar_angle(p):
        return (p[0] - start[0]) ** 2 + (p[1] - start[1]) ** 2, -orientation(
            start, p, (start[0], start[1] + 1)
        )

    sorted_points = sorted(points, key=polar_angle)

    # Construct the hull
    hull = [start]
    for p in sorted_points[1:]:
        while len(hull) > 1 and orientation(hull[-2], hull[-1], p) <= 0:
            hull.pop()
        hull.append(p)

    return hull


def is_inside_convex_hull(point, hull):
    """Check if a point is inside the convex hull"""
    for i in range(len(hull)):
        if orientation(hull[i], hull[(i + 1) % len(hull)], point) < 0:
            return False
    return True
