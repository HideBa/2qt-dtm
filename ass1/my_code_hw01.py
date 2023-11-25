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

        points = self.dt.points
        for point_i in range(1, len(points)):
            is_vertex_convex_hull = None
            # TODO: check what is the expected behaviour
            try:
                is_vertex_convex_hull = self.dt.is_vertex_convex_hull(point_i)
            except Exception as e:
                print(e)
                return []
            if is_vertex_convex_hull:
                continue

            incident_triangles = None
            try:
                incident_triangles = self.dt.incident_triangles_to_vertex(point_i)
            except Exception as e:
                print(e)
                continue

            for i in range(len(incident_triangles)):
                tri0 = incident_triangles[i]
                j = i + 1 if i + 1 < len(incident_triangles) else 0

                tri1 = incident_triangles[j]
                a0, b0, c0 = points[tri0[0]], points[tri0[1]], points[tri0[2]]
                a1, b1, c1 = points[tri1[0]], points[tri1[1]], points[tri1[2]]

                cc0 = circumcircle_center(a0, b0, c0)
                cc1 = circumcircle_center(a1, b1, c1)
                edge = [cc0, cc1]
                edges.append(edge)

        np_edges = np.array(edges)
        unique_edges = np.unique(np_edges, axis=0)
        edges_list = unique_edges.tolist()
        flatten_edges = [item for sublist in edges_list for item in sublist]
        return flatten_edges

    def interpolate_tin(self, x, y):
        """
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

        if not self.dt.is_inside_convex_hull(x, y):
            return np.nan

        triangle = self.dt.locate(x, y)

        p0_i, p1_i, p2_i = triangle[0], triangle[1], triangle[2]
        p0, p1, p2 = self.dt.points[p0_i], self.dt.points[p1_i], self.dt.points[p2_i]

        a0 = abs(area_triangle(q, p1, p2))
        a1 = abs(area_triangle(q, p0, p2))
        a2 = abs(area_triangle(q, p0, p1))
        area_total = a0 + a1 + a2
        print(area_total)
        w0, w1, w2 = a0 / area_total, a1 / area_total, a2 / area_total
        result = w0 * p0[2] + w1 * p1[2] + w2 * p2[2]

        result2 = self.dt.interpolate({"method": "TIN"}, [[x, y]])
        print("result: ", result)
        print("expected: ", result2)
        return result

    def get_area_voronoi_cell(self, vi):
        """
        Function that obtain the area of one Voronoi cells.

        Input:
            vi:     the position of the vertex in the TIN structure to display
        Output:
            z: the area of vi Voronoi cell,
               return numpy.inf if the cell is unbounded
               (infinity https://numpy.org/devdocs/reference/constants.html#numpy.inf)
        """

        if self.dt.is_vertex_convex_hull(vi):
            return np.inf

        try:
            incident_triangles = self.dt.incident_triangles_to_vertex(vi)
        except Exception as e:
            print(e)
            return np.inf

        voronoi_vertices = []
        for tri in incident_triangles:
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
    return (
        det3x3t(a, b, c) / 2.0
    )  # area can be minus. Signed should be handle by the caller function


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
        tri_area = area_triangle(arbitary_point, vertices[i], vertices[j])
        total += tri_area
    return total
