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
    v = (ax, ay)
    q = (bx, by)
    try:
        data = rasterio.open(d)
    except Exception as e:
        print(e)
        sys.exit()
    ras = data.read(1)
    nodata = data.nodata
    vq = bresenham_with_rasterio(data, v, q)

    return 1


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
    return re
    # re is a numpy with d.shape where the line is rasterised (values != 0)


if __name__ == "__main__":
    is_visible("./data/copernicus.tif", 83692.8, 447240.0, 85824.3, 448745.4)
