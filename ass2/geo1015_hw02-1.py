# -- geo1015.2023.hw02
# -- Hidemichi Baba
# -- 5967538

import argparse
import math
import rasterio
import sys
import numpy as np


def main():
    parser = argparse.ArgumentParser(description="My GEO1015.2023 hw02")
    parser.add_argument("cmd", choices=["aspect", "hillshade"])
    parser.add_argument("inputfile")
    args = parser.parse_args()

    file_name = extract_filename_from_path(args.inputfile)

    # -- load in memory the input DEM
    try:
        # -- this gives you a Rasterio dataset
        # -- https://rasterio.readthedocs.io/en/latest/quickstart.html
        d = rasterio.open(args.inputfile)
    except Exception as e:
        print(e)
        sys.exit()

    aspect_data, gradient_data = slope(d)
    if args.cmd == "aspect":
        print("Aspect!")
        save_ras(
            aspect_data,
            d,
            "./ass2/out/{}_aspect.tiff".format(file_name),
            nodata=d.nodata,
        )
    elif args.cmd == "hillshade":
        hillshade_data = hillshade(
            gradient_data,
            aspect_data,
        )
        print("Hillshade!")
        save_ras(
            hillshade_data,
            d,
            "./ass2/out/{}_hillshade.tiff".format(file_name),
            nodata=d.nodata,
        )


# MEMO: this function doens't consider nodata value
def hillshade(
    gradient_degree,
    aspect_degree,
    sun_azimuth_degree=315,
    sun_height_degree=45,
):
    gradient = np.radians(gradient_degree)
    aspect = np.radians(aspect_degree)

    hillshade = np.zeros_like(gradient, dtype=np.float32)

    if gradient.shape != aspect.shape:
        raise Exception("Gradient and Aspect should be same shape")

    if sun_azimuth_degree < 0 or sun_azimuth_degree > 360:
        raise Exception("invalid sun azimuth degree")

    if sun_height_degree < 0 or sun_height_degree >= 90:
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
                    * math.sin(gradient[i, j])
                    * math.cos(sun_azimuth - aspect[i, j])
                )
            )
            hillshade[i, j] = hillshade_ij if hillshade_ij > 0 else 0
    return hillshade


def slope(d):
    aspect, gradient = finite_difference(d)
    return aspect, gradient


# This function doesn't consider nodata value
def finite_difference(d):
    dtm = d.read(1)
    nodata = d.nodata
    cell_size, _ = calc_cellsize(d)
    aspect_list = np.zeros_like(dtm, dtype=np.float32)
    gradient_list = np.zeros_like(dtm, dtype=np.float32)
    n_rows, n_cols = dtm.shape
    for i in range(n_rows):
        for j in range(n_cols):
            if i == 0 or i == n_rows - 1 or j == 0 or j == n_cols - 1:
                aspect_list[i][j] = 0
                continue

            dx = (dtm[i, j - 1] - dtm[i, j + 1]) / (2 * cell_size)
            dy = (dtm[i + 1, j] - dtm[i - 1, j]) / (2 * cell_size)

            gradient = math.degrees(math.atan(math.sqrt(dx**2 + dy**2)))
            aspect = math.degrees(math.atan2(dy, dx))

            if dx > 0 and dy > 0:
                aspect = 90 - abs(aspect)
            elif dx > 0 and dy < 0:
                aspect = 90 + abs(aspect)
            elif dx < 0 and dy < 0:
                aspect = 90 + abs(aspect)
            elif dx < 0 and dy > 0:
                aspect = 450 - abs(aspect)
            elif dx == 0 and dy > 0:
                aspect = 0
            elif dx == 0 and dy < 0:
                aspect = 180
            elif dx > 0 and dy == 0:
                aspect = 90
            elif dx < 0 and dy == 0:
                aspect = 270
            elif dx == 0 and dy == 0:
                aspect = nodata
            gradient_list[i][j] = gradient
            aspect_list[i][j] = aspect
    return aspect_list, gradient_list


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


def extract_filename_from_path(path):
    return path.split("/")[-1].split(".")[0]


def calc_cellsize(d):
    width, height = d.transform[0], -d.transform[4]
    return (width, height)


if __name__ == "__main__":
    main()
