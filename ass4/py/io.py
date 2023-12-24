import os
import laspy
import numpy as np
import rasterio


def read_laz(file_path):
    with laspy.open(file_path) as f:
        print("header:", f.header)
        las = f.read()
        print("points:", len(las.points))
        print("dimensions:", list(las.point_format.dimension_names))
        return las


def clip_pc(las, bbox):  # bbox = [minx, miny, minz, maxx, maxy, maxz]
    x_invalid = (bbox[0] <= las.x) & (bbox[3] >= las.x)
    y_invalid = (bbox[1] <= las.y) & (bbox[4] >= las.y)
    z_invalid = (bbox[2] <= las.z) & (bbox[5] >= las.z)
    good_indices = np.where(x_invalid & y_invalid & z_invalid)
    clipped_points = las.points[good_indices].copy()
    return clipped_points


def write_ras(file_path, profile, data):
    with rasterio.open(file_path, "w", **profile) as dst:
        dst.write(data)


if __name__ == "__main__":
    read_laz("./data/thinned/LAS.las")
