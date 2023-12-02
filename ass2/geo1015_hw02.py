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

    file_name = extract_filename_from_path(args.inputfile)

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

    aspect_data, gradient_data = slope(d)
    hillshade_data = hillshade(gradient_data, aspect_data)

    save_ras(
        aspect_data,
        d,
        "./ass2/out/{}_aspect.tiff".format(file_name),
    )
    save_ras(hillshade_data, d, "./ass2/out/{}_hillshade.tiff".format(file_name))
    read_aspect()
    np.savetxt("./ass2/debug/aspect-my.csv", aspect_data, delimiter=",")


def hillshade(
    gradient_degree, aspect_degree, sun_azimuth_degree=315, sun_height_degree=30
):
    # it expects that all parameters in degree
    gradient = np.radians(gradient_degree)
    aspect = np.radians(aspect_degree)
    hillshade = np.zeros_like(gradient, dtype=np.float64)
    print("sun", sun_azimuth_degree, sun_azimuth_degree)

    if gradient.shape != aspect.shape:
        print("different size!!!")
        raise Exception("Gradient and Aspect should be same shape")

    if sun_azimuth_degree < 0 or sun_azimuth_degree > 360:
        raise Exception("invalid sun azimuth degree")

    if sun_height_degree < 0 or sun_height_degree > 180:
        raise Exception("invalid sun height")

    sun_azimuth = math.radians(sun_azimuth_degree)
    sun_height = math.radians(sun_height_degree)
    n_rows, n_cols = gradient.shape
    for i in range(n_rows):
        for j in range(n_cols):
            hillshade_ij = 255 * (
                (math.cos(math.pi / 2 - sun_height) * math.cos(gradient[i][j]))
                + (
                    math.sin(math.pi / 2 - sun_height)
                    * math.sin(gradient[i][j])
                    * math.cos(sun_azimuth - aspect[i][j])
                )
            )
            hillshade[i][j] = hillshade_ij
    return hillshade


def slope(d):
    aspect, gradient = finite_difference(d.read(1))
    return aspect, gradient


def finite_difference(dtm):
    aspect_list = np.zeros_like(dtm, dtype=np.float32)
    gradient_list = np.zeros_like(dtm, dtype=np.float32)
    n_rows, n_cols = dtm.shape
    for i in range(n_rows):
        for j in range(n_cols):
            if i == 0 or i == n_rows - 1 or j == 0 or j == n_cols - 1:
                aspect_list[i][j] = 0
                continue

            dx = (dtm[i, j + 1] - dtm[i, j - 1]) / (2 * CELL_SIZE)
            dy = (dtm[i + 1, j] - dtm[i - 1, j]) / (2 * CELL_SIZE)

            gradient = math.degrees(math.atan(math.sqrt(dx**2 + dy**2)))
            # TODO: consider when dx is zero
            aspect = math.degrees(math.atan2(dy, dx))
            gradient_list[i][j] = gradient
            aspect_list[i][j] = (aspect + 360) % 360 if aspect < 0 else aspect
    return aspect_list, gradient_list


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


def save_ras(data, source_ras, out_path):
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
    ) as dst:
        dst.write(data, 1)


def extract_filename_from_path(path):
    return path.split("/")[-1].split(".")[0]


"""
The code below is sample or for debug
"""


def read_aspect():
    with rasterio.open("./ass2/sample/aspect-qgis.tiff") as asp:
        asp_array = np.array(asp.read(), dtype=np.int64)
        reshaped = np.squeeze(asp_array, axis=0)
        np.savetxt("./ass2/debug/aspect-ans.csv", reshaped, delimiter=",")


if __name__ == "__main__":
    main()
