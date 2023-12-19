# -- my_code_hw03.py
# -- geo1015.2023.hw03
# -- Hidemichi Baba
# -- 5967538

import math
import sys
import unittest
import numpy as np
import rasterio
from rasterio import features


def is_visible(d, ax, ay, bx, by):
    """
    Is $a$ visible from $b$?

    Input:
        d: the rasterio input dataset
        ax:  x-coordinate of a
        ay:  y-coordinate of a
        bx:  x-coordinate of b
        by:  y-coordinate of b
    Output:
        1: visible
        0: not visible
        -1: $a$ and/or $b$ are outside the extent of the dataset
        -2: *a* and/or *b* are located in a no_data cell
    """
    try:
        data = rasterio.open(d)
    except Exception as e:
        print(e)
        sys.exit()
    v_row, v_col = data.index(ax, ay)
    q_row, q_col = data.index(bx, by)
    original_data = data.read(1)
    rows, cols = original_data.shape

    # If a or b is outside of the extent of the dataset
    if (not is_inside(0, rows - 1, 0, cols - 1, (v_row, v_col))) or (
        not is_inside(0, rows - 1, 0, cols - 1, (q_row, q_col))
    ):
        return -1
    v_z, q_z = original_data[v_row, v_col], original_data[q_row, q_col]
    nodata = data.nodata

    # If a or b is located in a no_data cell
    if v_z == nodata or q_z == nodata:
        return -2

    if v_row == q_row and v_col == q_col:
        return 1
    # Add 2.0 meter as person's height
    v, q = (ax, ay, v_z + 2.0), (bx, by, q_z)

    vq_profile = vq_profile_with_bresenham(data, v, q)
    for row in range(rows):
        for col in range(cols):
            if vq_profile[row, col] == nodata or original_data[row, col] == nodata:
                continue
            elif (row == v_row and col == v_col) or (row == q_row and col == q_col):
                continue
            elif original_data[row, col] >= vq_profile[row, col]:
                return 0
    return 1


def is_inside(min_row, max_row, min_col, max_col, row_col):
    return min_row <= row_col[0] <= max_row and min_col <= row_col[1] <= max_col


def vq_profile_with_bresenham(d, a, b):
    """
    This function is based on the Bresenham's line algorithm
    It recieves a rasterio dataset, and two points (a, b) in the form of (x, y, z)
    It returns a rasterio dataset with the same shape as the input dataset
    The values of the dataset are the interpolated height of the line connecting a and b
    """
    a_row, a_col = d.index(a[0], a[1])
    b_row, b_col = d.index(b[0], b[1])
    nodata = d.nodata
    # -- create in-memory a simple GeoJSON LineString
    v = {}
    v["type"] = "LineString"
    v["coordinates"] = []
    v["coordinates"].append(d.xy(a_row, a_col))
    v["coordinates"].append(d.xy(b_row, b_col))
    shapes = [(v, 1)]
    re = features.rasterize(
        shapes,
        out_shape=d.shape,
        transform=d.transform,
        all_touched=True,
        fill=nodata,
    )
    rows, cols = re.shape
    vq = VQ(a, b)
    vq_profile = np.zeros_like(re)
    for row in range(rows):
        for col in range(cols):
            if re[row, col] == nodata:
                vq_profile[row, col] = nodata
                continue
            intersection_point = vq.find_perpendicular_intersection(d.xy(row, col))
            val = vq.interpolate_height_on_linestring(intersection_point)
            vq_profile[row, col] = val
    return vq_profile


class VQ:
    # It expects v's height is added 2m as person's height
    def __init__(self, v, q):
        self.v = v
        self.q = q
        self.vq_dist = math.dist((self.v[0], self.v[1]), (self.q[0], self.q[1]))

    def interpolate_height_on_linestring(self, p):
        vp_dist = math.dist((self.v[0], self.v[1]), (p[0], p[1]))
        ratio = vp_dist / self.vq_dist
        height_p = self.v[2] + (self.q[2] - self.v[2]) * ratio
        return height_p

    def find_perpendicular_intersection(self, p):
        x1, y1, _ = self.v
        x2, y2, _ = self.q
        xp, yp = p
        if math.isclose(x2 - x1, 0):
            return x1, yp
        else:
            slope_vq = (y2 - y1) / (x2 - x1)

        if math.isclose(slope_vq, 0):
            return xp, y1
        else:
            slope_perpendicular = -1 / slope_vq

        x = (slope_perpendicular * xp - yp + y1 - slope_vq * x1) / (
            slope_perpendicular - slope_vq
        )
        y = slope_vq * (x - x1) + y1
        return x, y


def save_ras(data, source_ras, out_path, nodata=-9999):
    with rasterio.open(
        out_path,
        "w",
        driver="GTiff",
        height=data.shape[0],
        width=data.shape[1],
        count=1,
        dtype=source_ras.dtypes[0],
        crs=source_ras.crs,
        transform=source_ras.transform,
        nodata=nodata,
    ) as dst:
        dst.write(data, 1)


class Testing(unittest.TestCase):
    def test_is_inside(self):
        # Inside
        self.assertEqual(is_inside(0, 10, 0, 10, (5, 5)), True)
        # Boundary
        self.assertEqual(is_inside(0, 10, 0, 10, (0, 0)), True)
        self.assertEqual(is_inside(0, 10, 0, 10, (10, 10)), True)
        # Outside
        self.assertEqual(is_inside(0, 10, 0, 10, (11, -1)), False)

    def test_is_visible(self):
        # Outside of extent: Should return -1
        self.assertEqual(
            is_visible(
                "./ass3/data/copernicus.tif", 84874.9, 449864.2, 86843.2, 449977.8
            ),
            -1,
        )
        self.assertEqual(
            is_visible(
                "./ass3/data/copernicus.tif", 86843.2, 449977.8, 84874.9, 449864.2
            ),  # opposite order
            -1,
        )
        # On no data value: should return -2
        self.assertEqual(
            is_visible("./ass3/data/ahn.tif", 81384.8, 444480.7, 83556.6, 449647.9),
            -2,  # Opposite order
        )

        # Visible, same cell
        self.assertEqual(
            is_visible(
                "./ass3/data/copernicus.tif",
                84535.14,
                447598.66,
                84536.53,
                447598.83,
            ),
            1,
        )
        self.assertEqual(
            is_visible(
                "./ass3/data/copernicus.tif",
                84527.10,
                447602.81,  # Delft church, opposite order
                84639.05,
                447500.85,
            ),
            1,
        )
        self.assertEqual(
            is_visible(
                "./ass3/data/ahn.tif", 84495.5, 447579.4, 84170.2, 447627.4
            ),  # Delft church
            1,
        )
        # # # Not visible
        self.assertEqual(
            is_visible(
                "./ass3/data/copernicus.tif", 84915.2, 447669.1, 84573.7, 447444.8
            ),
            0,
        )
        self.assertEqual(
            is_visible("./ass3/data/ahn.tif", 84408.01, 447532.81, 84869.3, 447785.9),
            0,
        )
        self.assertEqual(
            is_visible("./ass3/data/ahn.tif", 84869.3, 447785.9, 84408.01, 447532.81),
            0,
        )


if __name__ == "__main__":
    unittest.main()
