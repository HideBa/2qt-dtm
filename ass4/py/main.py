from ass4.py.io import read_laz
from ass4.py.point_cloud import GFTIN
from ass4.py.tin import TIN


def create_dtm(input_file, output_file):
    las = read_laz(input_file)

    bbox = las.header.min + las.header.max
    print("bbox:", bbox)
    gftin = GFTIN(100, las.points, bbox, False)

    ground_points = gftin.ground_filtering()

    # print static info of the point cloud
    print("ground points:", len(ground_points))
    print("ground points shape:", ground_points.shape)
    print("ground points dtype:", ground_points.dtype)

    # write ground points to a file
    tin = TIN(ground_points)
    tin.write_dtm(output_file)


if __name__ == "__main__":
    create_dtm("./data/thinned/LAS.las", "./data/out/dtm.tif")
