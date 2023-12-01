# -- geo1015.2023.hw02
# -- Hidemichi Baba
# -- 5967538

import argparse
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
    # some_code_to_help_with_rasterio(d, middlept)
    gradient_ras = gradient(d)


def aspect(d):
    pass


def maximum_height_difference(d):
    n1 = d.read(1)  # It expects it's single band

    n_rows, n_cols = n1.shape
    for i in range(n_rows):
        for j in range(n_cols):
            row_min = max(i - 1, 0)
            row_max = min(i + 1, n_rows - 1)
            col_min = max(j - 1, 0)
            col_max = min(j + 1, n_cols - 1)

            neighbours = n1[row_min : row_max + 1, col_min : col_max + 1]
            height_diff = [abs(height - n1[i][j]) for height in neighbours]
            print("nei", neighbours)


def gradient(d):
    print("name", d.name)
    print("mode", d.mode)
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
    print("grad", gradient_list.shape)

    n2 = np.zeros_like(n1, dtype=np.int8)


# def neighbour_gradient(neighbours):
#     center_index = len(neighbours)/2
#     for n in neighbours:
#         if index()


def hillshade(d):
    pass


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


if __name__ == "__main__":
    main()
