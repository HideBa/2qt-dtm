# -- geo1015.2023.hw02
# -- Hidemichi Baba
# -- 5967538

import argparse
import rasterio
import sys
import numpy as np


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
    some_code_to_help_with_rasterio(d, middlept)


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
