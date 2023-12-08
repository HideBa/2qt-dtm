# -- my_code_hw03.py
# -- geo1015.2023.hw03
# -- [YOUR NAME]
# -- [YOUR STUDENT NUMBER]

import math
import sys
import numpy as np
import rasterio
from rasterio import features


def is_visible(d, ax, ay, bx, by):
    """
    !!! TO BE COMPLETED !!!

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

    # TODO: add error handling

    ras = data.read(1)
    v_z, q_z = ras[v_row, v_col], ras[q_row, q_col]
    # Add 2.0 meter as person's height
    v, q = (ax, ay, v_z + 2.0), (bx, by, q_z)

    nodata = data.nodata
    vq_profile = bresenham_with_rasterio(data, v, q)

    rows, cols = ras.shape
    for row in range(rows):
        for col in range(cols):
            if vq_profile[row, col] == nodata or ras[row, col] == nodata:
                continue

            if ras[row, col] >= vq_profile[row, col]:
                return False
    save_ras(vq_profile, data, "./data/out/breshenham.tif")
    # Memo: add 2m as person's height
    return True


def bresenham_with_rasterio(d, a, b):
    """
    !!! USE THIS CODE !!!

    Example code that can be useful: use it for your function,
    copy part of it, it's allowed.
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
        # all_touched=True,
        transform=d.transform,
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
            intersection_point = find_perpendicular_intersection(a, b, d.xy(row, col))
            val = vq.interpolate_height_on_linestring(intersection_point)
            vq_profile[row, col] = val
    return vq_profile
    # re is a numpy with d.shape where the line is rasterised (values != 0)


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


def find_perpendicular_intersection(v, q, p):
    x1, y1 = v
    x2, y2 = q
    xp, yp = p
    if x2 - x1 != 0:  # TODO: check floating point
        slope_vq = (y2 - y1) / (x2 - x1)
    else:
        return x1, yp

    if slope_vq != 0:
        slope_perpendicular = -1 / slope_vq
    else:
        return xp, y1

    # Equation of line VQ: y = slope_vq * (x - x1) + y1
    # Equation of perpendicular from P: y = slope_perpendicular * (x - xp) + yp

    # Solve for x and y
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


if __name__ == "__main__":
    is_visible("./data/copernicus.tif", 83692.8, 447240.0, 85824.3, 448745.4)
