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

            # If the triangle contains vertices on a convex hull, it's voronoi is unbounded(unnecessary to draw edges)
            if self.any_vertices_convex_hull([tri[0], tri[1], tri[2]]):
                continue
            a0 = self.dt.points[tri[0]]
            b0 = self.dt.points[tri[1]]
            c0 = self.dt.points[tri[2]]

            cc0 = circumcircle_center(a0, b0, c0)
            for a_tri in adjacent_triangles:
                if a_tri in visited_triangles:
                    continue
                a1 = self.dt.points[a_tri[0]]
                if self.any_vertices_convex_hull([a_tri[0], a_tri[1], a_tri[2]]):
                    continue
                b1 = self.dt.points[a_tri[1]]
                c1 = self.dt.points[a_tri[2]]
                cc1 = circumcircle_center(a1, b1, c1)

                if cc1 is None or cc0 is None:
                    continue

                edge = [cc1, cc0]
                edges.append(edge)
            # TODO: check if we should add convex hull edges
        # np_edges = np.array(edges)
        # unique_edges = np.unique(np_edges, axis=0)
        # edges_list = unique_edges.tolist()
        # flatten_edges = [item for sublist in edges_list for item in sublist]
        flatten_edges = [item for sublist in edges for item in sublist]
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

        # TODO: check if it allowed or not
        if not self.dt.is_inside_convex_hull(x, y):
            return np.nan
            # raise ValueError("Point is outside the convex hull")

        triangle = self.dt.locate(x, y)

        p0_i, p1_i, p2_i = triangle[0], triangle[1], triangle[2]
        p0, p1, p2 = self.dt.points[p0_i], self.dt.points[p1_i], self.dt.points[p2_i]

        a0 = abs(area_triangle(q, p1, p2))
        a1 = abs(area_triangle(q, p0, p2))
        a2 = abs(area_triangle(q, p0, p1))
        area_total = a0 + a1 + a2

        w0, w1, w2 = a0 / area_total, a1 / area_total, a2 / area_total
        result = w0 * p0[2] + w1 * p1[2] + w2 * p2[2]

        result2 = self.dt.interpolate({"method": "TIN"}, [[x, y]])
        print("res1---", result)
        print("expected---", result2)
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
        try:
            incident_triangles = self.dt.incident_triangles_to_vertex(vi)
        except Exception as e:
            print("vi is not in the TIN", e)
            return np.inf

        voronoi_vertices = []
        for tri in incident_triangles:
            # TODO: check later
            if not self.dt.is_finite(tri):
                return np.inf
            p0_i, p1_i, p2_i = tri
            p0, p1, p2 = (
                self.dt.points[p0_i],
                self.dt.points[p1_i],
                self.dt.points[p2_i],
            )
            cc = circumcircle_center(p0, p1, p2)
            voronoi_vertices.append(cc)
        voronoi_simple_polygon = voronoi_vertices + [voronoi_vertices[0]]
        area = area_polygon(voronoi_simple_polygon)

        return area

    def any_vertices_convex_hull(self, vertices):
        for v in vertices:
            if self.dt.is_vertex_convex_hull(v):
                return True
            else:
                continue
        return False

    # TODO: change to implement this ref: https://github.com/hugoledoux/startin/blob/574e3c8cd06aa5b03b86f867b1fb69f21c0f81c5/src/geom/mod.rs#L18C3-L18C3


def circumcircle_center(p1, p2, p3):
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
    return [ux, uy]


def area_triangle(a, b, c):
    return det3x3t(a, b, c) / 2.0


# Ref: https://github.com/hugoledoux/startin/blob/574e3c8cd06aa5b03b86f867b1fb69f21c0f81c5/src/geom/mod.rs#L10
def det3x3t(a, b, c):
    return ((a[0] - c[0]) * (b[1] - c[1])) - ((a[1] - c[1]) * (b[0] - c[0]))


def area_polygon(
    vertices,
):  # vertices should be simple feature data format. e.g. first and last should be the same vertext
    arbitary_point = [
        0,
        0,
    ]  # this is an arbitary point to calculate the area of polygon
    total = 0.0
    for i in range(len(vertices) - 1):
        j = i + 1
        tri_area = abs(area_triangle(arbitary_point, vertices[i], vertices[j]))
        total += tri_area
    return total
