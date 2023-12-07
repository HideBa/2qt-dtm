# -- geo1015.2023.hw02
# -- Hidemichi Baba
# -- 5967538

import argparse
import math
import rasterio
import sys
import numpy as np
import startinpy


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
    # if args.cmd == "aspect":
    #     print("Aspect!")
    #     save_ras(
    #         aspect_data,
    #         d,
    #         "./ass2/out/{}_aspect.tiff".format(file_name),
    #         nodata=d.nodata,
    #     )
    # elif args.cmd == "hillshade":
    #     hillshade_data = hillshade(gradient_data, aspect_data, d.nodata)
    #     print("Hillshade!")
    #     save_ras(
    #         hillshade_data,
    #         d,
    #         "./ass2/out/{}_hillshade.tiff".format(file_name),
    #         nodata=d.nodata,
    #     )

    hillshade_data = hillshade(gradient_data, aspect_data)
    save_ras(
        aspect_data,
        d,
        "./ass2/out/{}_aspect.tiff".format(file_name),
        nodata=d.nodata,
    )
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


# def hillshade2(
#     gradient_degree,
#     aspect_degree,
#     nodata=-9999,
#     sun_azimuth_degree=315,
#     sun_height_degree=45,
# ):
#     gradient = np.zeros_like(gradient_degree)
#     aspect = np.zeros_like(aspect_degree)
#     row, col = gradient_degree.shape
#     for i in range(row):
#         for j in range(col):
#             gradient[i, j] = (
#                 math.radians(gradient_degree[i, j])
#                 if gradient_degree[i, j] != nodata
#                 else nodata
#             )
#             aspect[i, j] = (
#                 math.radians(aspect_degree[i, j])
#                 if aspect_degree[i, j] != nodata
#                 else nodata
#             )

#     # gradient = np.radians(gradient_degree)
#     # aspect = np.radians(aspect_degree)
#     hillshade = np.zeros_like(gradient, dtype=np.float64)
#     print("nodata: ", nodata)

#     if gradient.shape != aspect.shape:
#         raise Exception("Gradient and Aspect should be same shape")

#     if sun_azimuth_degree < 0 or sun_azimuth_degree > 360:
#         raise Exception("invalid sun azimuth degree")

#     if sun_height_degree < 0 or sun_height_degree >= 90:
#         raise Exception("invalid sun height")

#     sun_azimuth = math.radians(sun_azimuth_degree)
#     sun_height = math.radians(sun_height_degree)
#     n_rows, n_cols = gradient.shape
#     for i in range(n_rows):
#         for j in range(n_cols):
#             if gradient[i, j] == nodata or aspect[i, j] == nodata:
#                 print("nodata!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
#                 hillshade[i, j] = nodata
#                 continue
#             hillshade_ij = 255 * (
#                 (math.cos(math.pi / 2 - sun_height) * math.cos(gradient[i][j]))
#                 + (
#                     math.sin(math.pi / 2 - sun_height)
#                     * math.sin(gradient[i, j])
#                     * math.cos(sun_azimuth - aspect[i, j])
#                 )
#             )

#             hillshade[i, j] = hillshade_ij
#     return hillshade


def slope(d):
    aspect, gradient = tin_slope(d)
    # aspect, gradient = maximum_height_difference(d)
    # aspect, gradient = finite_difference(d)
    # aspect, gradient = local_polynominal_fitting(d)

    return aspect, gradient


def tin_slope(d):
    points = convert_raster_to_points(d)
    points = np.array(points)
    # flatten list
    # [(x, y, z), (x, y, z), ...]
    np_points = points.reshape(-1, 3)
    print("np_points: ", np_points[0:100])
    print("np_points.shape: ", np_points.shape)
    dt = startinpy.DT()
    # print("np points: ", np_points)
    dt.insert(np_points)
    for i in range(len(points)):
        if i > 10:
            continue
        for j in range(len(points[i])):
            if i > 10:
                continue
            if i > len(points) or j > len(points):
                continue
            index_of_p = i * len(points[i]) + j
            incident_triangles = dt.incident_triangles_to_vertex(index_of_p)
            normal_vectors = []
            for tri in incident_triangles:
                p0 = dt.points[tri[0]]
                p1 = dt.points[tri[1]]
                p2 = dt.points[tri[2]]
                # print("tri", tri)
                # print("p0: ", p0)
                # print("p1: ", p1)
                # print("p2: ", p2)
                e01 = p1 - p0
                e02 = p2 - p0
                normal = np.cross(e01, e02)
                normal_vectors.append(normal / np.linalg.norm(normal))
            sum_normal_vector = np.sum(normal_vectors, axis=0) / len(normal_vectors)
            ave_normal_vector = sum_normal_vector / np.linalg.norm(sum_normal_vector)

            # print("ave_normal_vector: ", ave_normal_vector)
            aspect_radians = np.arctan2(ave_normal_vector[0], ave_normal_vector[1])

            # Convert to degrees and adjust to [0, 360)
            aspect_degrees = np.degrees(aspect_radians)
            aspect_degrees = (aspect_degrees + 360) % 360
            # print("aspect_degrees: ", aspect_degrees)
    return None, None


# This function doesn't consider nodata value
def finite_difference(d):
    dtm = d.read(1)
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
            gradient_list[i][j] = gradient
            aspect_list[i][j] = aspect
    return aspect_list, gradient_list


# def finite_difference(d):
#     dtm = d.read(1)
#     nodata = d.nodata
#     aspect_list = np.zeros_like(dtm, dtype=np.float32)
#     gradient_list = np.zeros_like(dtm, dtype=np.float32)
#     n_rows, n_cols = dtm.shape
#     for i in range(n_rows):
#         for j in range(n_cols):
#             if dtm[i][j] == nodata:
#                 aspect_list[i][j] = nodata
#                 gradient_list[i][j] = nodata
#                 continue
#             if i == 0 or i == n_rows - 1 or j == 0 or j == n_cols - 1:
#                 aspect_list[i][j] = 0
#                 continue

#             dx = (dtm[i, j - 1] - dtm[i, j + 1]) / (2 * CELL_SIZE)
#             dy = (dtm[i + 1, j] - dtm[i - 1, j]) / (2 * CELL_SIZE)

#             gradient = math.degrees(math.atan(math.sqrt(dx**2 + dy**2)))
#             aspect = math.degrees(math.atan2(dy, dx))


#             if dx > 0 and dy > 0:
#                 aspect = 90 - abs(aspect)
#             elif dx > 0 and dy < 0:
#                 aspect = 90 + abs(aspect)
#             elif dx < 0 and dy < 0:
#                 aspect = 90 + abs(aspect)
#             elif dx < 0 and dy > 0:
#                 aspect = 450 - abs(aspect)
#             elif dx == 0 and dy > 0:
#                 aspect = 0
#             elif dx == 0 and dy < 0:
#                 aspect = 180
#             elif dx > 0 and dy == 0:
#                 aspect = 90
#             elif dx < 0 and dy == 0:
#                 aspect = 270
#             gradient_list[i][j] = gradient
#             aspect_list[i][j] = aspect
#     return aspect_list, gradient_list


def maximum_height_difference(d):
    n1 = d.read(1)
    aspect = np.zeros_like(n1, dtype=np.uint16)
    gradient = np.zeros_like(n1, dtype=np.float32)
    cell_size, _ = calc_cellsize(d)
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
                    height_diff = abs(abs(center) - abs(n))
                    height_diffs.append([height_diff, azimuthal_degree])
                else:
                    height_diffs.append([0, azimuthal_degree])
            max_neighbour = max(height_diffs, key=lambda x: x[0])
            azimuthal_degree = max_neighbour[1]
            distance = (
                cell_size
                if azimuthal_degree % 90 == 0
                else math.sqrt(cell_size**2 + cell_size**2)
            )
            gradient_ij = math.degrees(math.atan(max_neighbour[0] / distance))
            aspect[i][j] = azimuthal_degree
            gradient[i][j] = gradient_ij
    return (aspect, gradient)


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


def calc_cellsize(d):
    width, height = d.transform[0], -d.transform[4]
    return (width, height)


if __name__ == "__main__":
    main()
