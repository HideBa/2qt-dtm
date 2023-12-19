# -- geo1015_hw03.py
# -- geo1015.2023.hw03
# -- 2023-12-07
# -- Hugo Ledoux <h.ledoux@tudelft.nl>


# ------------------------------------------------------------------------------
# DO NOT MODIFY THIS FILE!!!
# ------------------------------------------------------------------------------
# pip install rasterio
# ------------------------------------------------------------------------------

import sys
import rasterio
import argparse

import my_code_hw03


def main():
    parser = argparse.ArgumentParser(description="Performs line-of-sight queries")
    parser.add_argument("inputfile", help="a GDAL-readable raster terrain in EPSG:7415")
    parser.add_argument("ax", type=float, help="x-coord of a")
    parser.add_argument("ay", type=float, help="y-coord of a")
    parser.add_argument("bx", type=float, help="x-coord of b")
    parser.add_argument("by", type=float, help="y-coord of b")
    args = parser.parse_args()

    # -- load in memory the input grid
    try:
        # -- this gives you a Rasterio dataset
        # -- https://rasterio.readthedocs.io/en/latest/quickstart.html
        d = rasterio.open(args.inputfile)
    except Exception as e:
        print(e)
        sys.exit()

    print(d.crs)

    # -- make sure it's EPSG:7415
    if d.crs != "EPSG:7415":
        print("The input dataset must be EPSG:7415 (now it's {})".format(d.crs))
        sys.exit()

    re = my_code_hw03.is_visible(d, args.ax, args.ay, args.bx, args.by)
    if re == 1:
        print("YES")
    elif re == 0:
        print("NO")
    elif re == -1:
        print("a and/or b are outside the extent of the dataset")
    elif re == -2:
        print("a and/or b are located in a no_data cell")
    else:
        print("Unknown error")  # -- this should never happen!


if __name__ == "__main__":
    main()
