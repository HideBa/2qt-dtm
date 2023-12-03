import numpy as np
import rasterio
from rasterio.enums import Resampling


def raster_stats(ground_truth_file, measured_file):
    """
    Calculate the mean and standard deviation of a raster.
    """
    # Open the raster
    ground_truth = rasterio.open(ground_truth_file)
    measured = rasterio.open(measured_file)
    measured, _ = resample_raster(measured, ground_truth)
    ground_truth_b1 = np.array(ground_truth.read(1), dtype=np.float64)
    measured_b1 = np.array(np.squeeze(measured), dtype=np.float64)

    rmse = np.sqrt(np.mean((ground_truth_b1 - measured_b1) ** 2))

    print("RMSE: {}".format(round(rmse, 2)))


def resample_raster(source, target):
    """Resample a raster to match the target shape."""
    data = source.read(
        out_shape=target.shape,
        resampling=Resampling.bilinear,
    )
    transform = source.transform * source.transform.scale(
        (source.width / data.shape[-1]), (source.height / data.shape[-2])
    )

    return data, transform


if __name__ == "__main__":
    raster_stats("./ass2/clipped-ahn.tif", "./ass2/clipped-copernicus.tif")
