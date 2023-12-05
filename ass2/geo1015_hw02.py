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
    gradient_degree, aspect_degree, sun_azimuth_degree=315, sun_height_degree=45
):
    # it expects that all parameters in degree
    gradient = np.radians(gradient_degree)
    aspect = np.radians(aspect_degree)
    hillshade = np.zeros_like(gradient, dtype=np.float64)

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
    aspect, gradient = finite_difference(d)
    # aspect, gradient = maximum_height_difference(d)
    return aspect, gradient


def tin_slope(d):
    points = convert_raster_to_points(d)
    dt = statingpy.DT()
    dt.insert(points)
    for i in range(len(points)):
        for j in range(len(points[i])):
            if i > len(points) or j > len(points):
                continue
            index_of_p = i * len(points[i]) + j
            incident_triangles = dt.incident_triangles_to_vertex(index_of_p)
            normal_vectors = []
            for tri in incident_triangles:
                p0 = dt.poinst[tri[0]]
                p1 = dt.poinst[tri[1]]
                p2 = dt.poinst[tri[2]]
                e01 = p1 - p0
                e02 = p2 - p0
                normal = np.cross(e01, e02)
                normal_vectors.append(normal)
            normal_vector = np.mean(
                normal_vectors, axis=0
            )  # TODO: check if this is correct


def finite_difference(d):
    dtm = d.read(1)
    aspect_list = np.zeros_like(dtm, dtype=np.float32)
    gradient_list = np.zeros_like(dtm, dtype=np.float32)
    n_rows, n_cols = dtm.shape
    for i in range(n_rows):
        for j in range(n_cols):
            if i == 0 or i == n_rows - 1 or j == 0 or j == n_cols - 1:
                aspect_list[i][j] = 0
                continue

            dx = (dtm[i, j - 1] - dtm[i, j + 1]) / (2 * CELL_SIZE)
            dy = (dtm[i + 1, j] - dtm[i - 1, j]) / (2 * CELL_SIZE)

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
            gradient_list[i][j] = gradient
            aspect_list[i][j] = aspect
    return aspect_list, gradient_list


def convert_cartesian_to_azimuthal(cartesian_degree):
    if 0 <= cartesian_degree < 90:
        return 90 - cartesian_degree
    elif 90 <= cartesian_degree <= 180:
        return 450 - cartesian_degree
    elif -90 <= cartesian_degree < 0:
        return 90 + abs(cartesian_degree)
    elif -180 <= cartesian_degree < -90:
        return 90 + abs(cartesian_degree)


def maximum_height_difference(d):
    n1 = d.read(1)
    aspect = np.zeros_like(n1, dtype=np.uint16)
    gradient = np.zeros_like(n1, dtype=np.float32)
    n_rows, n_cols = n1.shape
    for i in range(n_rows):
        for j in range(n_cols):
            center = n1[i][j]
            height_diffs = []
            for di, dj, azimuthal_degree in [
                (-1, -1, 315),
                (-1, 0, 0),
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
                    height_diffs.append([height_diff, azimuthal_degree])
                else:  # TODO: check how should this be handled
                    height_diffs.append([0, azimuthal_degree])
            max_neighbour = max(height_diffs, key=lambda x: x[0])
            azimuthal_degree = max_neighbour[1]
            distance = (
                CELL_SIZE
                if azimuthal_degree % 90 == 0
                else math.sqrt(CELL_SIZE**2 + CELL_SIZE**2)
            )
            gradient_ij = math.degrees(math.atan(max_neighbour[0] / distance))
            aspect[i][j] = azimuthal_degree
            gradient[i][j] = gradient_ij

    return (aspect, gradient)


# def local_polynominal_fitting(d):


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


def triangulate_grid_points(points_row_col):
    triangles = []
    for i in range(len(points_row_col)):
        lst = []
        for j in range(len(points_row_col[i])):
            if i > len(points_row_col) or j > len(points_row_col):
                continue
            p1 = points_row_col[i][j]
            p2 = points_row_col[i][j + 1]
            p3 = points_row_col[i + 1][j]
            lst.append([p1, p2, p3])
        triangles.append(lst)


def convert_raster_to_points(d):
    width, height = d.width, d.height

    # Get the transformation matrix
    transform = d.transform
    data = d.read(1)
    centers = []
    for row in range(height):
        lst = []
        for col in range(width):
            # Calculate the center coordinates
            centerX = transform[2] + transform[0] * (col + 0.5)
            centerY = transform[5] + transform[4] * (row + 0.5)
            lst.append((centerX, centerY, data[row, col]))
        centers.append(lst)
    return centers


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
