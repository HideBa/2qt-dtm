# -- geo1015.2023.hw02
# -- Hidemichi Baba
# -- 5967538

import argparse
import math
import rasterio
import sys
import numpy as np

CELL_SIZE = 30  # in meters


def main():
    parser = argparse.ArgumentParser(description="My GEO1015.2023 hw02")
    parser.add_argument("cmd", choices=["aspect", "hillshade"])
    parser.add_argument("inputfile")
    args = parser.parse_args()

    if args.cmd == "aspect":
        print("Aspect!")
    elif args.cmd == "hillshade":
        print("Hillshade!")

    # -- load in memory the input DEM
    try:
        # -- this gives you a Rasterio dataset
        # -- https://rasterio.readthedocs.io/en/latest/quickstart.html
        d = rasterio.open(args.inputfile)
    except Exception as e:
        print(e)
        sys.exit()

    print("name:", d.name)
    print("crs:", d.crs)
    print("size:", d.shape)

    bbox = d.bounds
    middlept = ((bbox[2] - bbox[0]) / 2 + bbox[0], (bbox[3] - bbox[1]) / 2 + bbox[1])
    print(middlept)

    debug_d = np.squeeze(d.read(1))
    np.savetxt("./ass2/debug/terrain.csv", debug_d, delimiter=",")

    aspect_data = aspect(d)
    with rasterio.open(
        "./ass2/out/aspect.tiff",
        "w",
        driver="GTiff",
        height=aspect_data.shape[0],
        width=aspect_data.shape[1],
        count=1,
        dtype=np.uint16,
        crs=d.crs,
        transform=d.transform,
    ) as dst:
        dst.write(aspect_data, 1)
    read_aspect()
    np.savetxt("./ass2/debug/aspect-my.csv", aspect_data, delimiter=",")


def aspect(d):
    # return maximum_height_difference(d)
    aspect, _ = finite_difference(d)
    return aspect


def finite_difference(d):
    n1 = d.read(1)
    aspect_list = np.zeros_like(n1, dtype=np.float64)
    gradient_list = np.zeros_like(n1, dtype=np.float64)
    n_rows, n_cols = n1.shape
    for i in range(n_rows):
        for j in range(n_cols):
            if i == 0 or i == n_rows - 1 or j == 0 or j == n_cols - 1:
                aspect_list[i][j] = 0
                continue

            dx = (n1[i - 1][j] - n1[i + 1][j]) / (2 * CELL_SIZE)
            dy = (n1[i][j - 1] - n1[i][j + 1]) / (2 * CELL_SIZE)
            gradient = math.atan(math.sqrt(dx**2 + dx**2))
            # TODO: check when delta_z_x is 0
            aspect = math.atan2(dy, dx)
            gradient_list[i][j] = gradient
            aspect_list[i][j] = aspect
    aspect_in_degree = np.degrees(aspect_list) % 360
    return aspect_in_degree, gradient_list


def maximum_height_difference(d):
    n1 = d.read(1)  # It expects it's single band
    aspect = np.zeros_like(n1, dtype=np.uint16)
    n_rows, n_cols = n1.shape
    for i in range(n_rows):
        for j in range(n_cols):
            center = n1[i][j]
            height_diffs = []
            for di, dj, degree in [
                (-1, -1, 315),
                (-1, 0, 360),
                (-1, 1, 45),
                (0, -1, 270),
                (0, 1, 90),
                (1, -1, 225),
                (1, 0, 180),
                (1, 1, 135),
            ]:
                ni, nj = i + di, j + dj
                if 0 <= ni < n_rows and 0 <= nj < n_cols:
                    n = n1[ni][nj]
                    height_diff = abs(center - n)
                    height_diffs.append([height_diff, degree])
                else:  # TODO: check how should this be handled
                    height_diffs.append([0, degree])
            max_neighbour = max(height_diffs, key=lambda x: x[0])
            degree = max_neighbour[1]
            aspect[i][j] = degree
    print("min", np.min(aspect))
    print("max", np.max(aspect))
    return aspect


def gradient(d):
    n1 = d.read(1)  # It expects it's single band

    n_rows, n_cols = n1.shape
    count = 0
    # for i in range(n_rows):
    #     for j in range(n_cols):
    #         if count > 1:
    #             continue
    #         row_min = max(i - 1, 0)
    #         row_max = min(i + 1, n_rows - 1)
    #         col_min = max(j - 1, 0)
    #         col_max = min(j + 1, n_cols - 1)

    #         neighbours = n1[row_min : row_max + 1, col_min : col_max + 1]
    #         print("nei", neighbours)
    #         count += 1
    gradient_list = np.array(np.gradient(n1, CELL_SIZE))

    n2 = np.zeros_like(n1, dtype=np.int8)


# def neighbour_gradient(neighbours):
#     center_index = len(neighbours)/2
#     for n in neighbours:
#         if index()


def hillshade(d):
    pass


"""
The code below is sample or for debug
"""


def some_code_to_help_with_rasterio(dataset, middlept):
    """
    !!! USE THIS CODE !!!

    Some random operations with rasterio are shown below, they don't have
    much meanings.
    They are useful to learn how to read/write GeoTIFF files.
    Use this code for your own function, copy part of it, it's allowed.
    """
    # -- numpy of input
    n1 = dataset.read(1)
    # -- an empty array with all values=0
    # n2 = np.zeros(dataset.shape, dtype=np.int8) #-- you can define the type to use for each cell
    n2 = np.zeros(dataset.shape)
    for i in range(n1.shape[0]):
        for j in range(n1.shape[1]):
            n2[i][j] = 2 * n1[i][j]
    # -- put middlept value=99
    # -- index of p in the numpy raster
    row, col = dataset.index(middlept[0], middlept[1])
    n2[row, col] = 999
    # -- write this to disk
    output_file = "output.tiff"
    with rasterio.open(
        output_file,
        "w",
        driver="GTiff",
        height=n2.shape[0],
        width=n2.shape[1],
        count=1,
        dtype=n2.dtype,
        crs=dataset.crs,
        transform=dataset.transform,
    ) as dst:
        dst.write(n2, 1)
    print("File written to '%s'" % output_file)


def read_aspect():
    with rasterio.open("./ass2/sample/aspect-qgis.tiff") as asp:
        asp_array = np.array(asp.read(), dtype=np.int64)
        reshaped = np.squeeze(asp_array, axis=0)
        np.savetxt("./ass2/debug/aspect-ans.csv", reshaped, delimiter=",")


if __name__ == "__main__":
    main()
