import math
import unittest

import numpy as np
from my_code_hw01 import Tin, area_polygon, circumcircle_center, det3x3t


class Testing(unittest.TestCase):
    def test_area_polygon(self):
        # Test case 1: Empty list of vertices
        vertices = []
        expected_area = 0.0
        self.assertEqual(area_polygon(vertices), expected_area)

        # Test case 2: Single vertex
        vertices = [(1, 2)]
        expected_area = 0.0
        self.assertEqual(area_polygon(vertices), expected_area)

        # Test case 3: Colinear
        vertices = [(1, 2), (3, 4), (5, 6), (1, 2)]
        expected_area = 0.0
        self.assertEqual(area_polygon(vertices), expected_area)

        # Test case 4: Triangle
        vertices = vertices = [(0, 0), (2, 0), (1, 1), (0, 0)]
        expected_area = 1
        self.assertEqual(area_polygon(vertices), expected_area)

        # Test case 5: Quadrilateral
        vertices = [(0, 0), (2, 0), (2, 1), (0, 1), (0, 0)]
        expected_area = 2
        self.assertEqual(area_polygon(vertices), expected_area)

    def test_interpolate_tin(self):
        tin = Tin()
        tin.insert_one_pt(0, 0, 0)
        tin.insert_one_pt(1, 0, 1)
        tin.insert_one_pt(0, 1, 2)
        tin.insert_one_pt(1, 1, 3)
        tin.insert_one_pt(0.5, 0.5, 4)
        tin.insert_one_pt(0.5, 0.25, 5)
        tin.insert_one_pt(0.25, 0.5, 6)

        # Test1: inside of the triangle
        x = 0.5
        y = 0.5
        expected = tin.dt.interpolate({"method": "TIN"}, [[x, y]])
        self.assertEqual(round(tin.interpolate_tin(x, y), 5), round(expected[0], 5))

        # Test2: inside of the triangle
        x = 0.7
        y = 0.7
        expected = tin.dt.interpolate({"method": "TIN"}, [[x, y]])
        self.assertEqual(round(tin.interpolate_tin(x, y), 5), round(expected[0], 5))

        # Test3: outside of the triangle
        x = 10
        y = 10
        expected = tin.dt.interpolate({"method": "TIN"}, [[x, y]])
        self.assertTrue(np.isnan(tin.interpolate_tin(x, y)))

        # Test4: outside of the triangle
        x = np.Infinity
        y = np.Infinity
        expected = tin.dt.interpolate({"method": "TIN"}, [[x, y]])
        self.assertTrue(np.isnan(tin.interpolate_tin(x, y)))


if __name__ == "__main__":
    unittest.main()
