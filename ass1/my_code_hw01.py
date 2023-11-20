# -- my_code_hw01.py
# -- geo1015.2023.hw01
# -- [YOUR NAME]
# -- [YOUR STUDENT NUMBER]

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
        !!! TO BE COMPLETED !!!

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
        return edges

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
        return 123.45

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
        return np.inf
