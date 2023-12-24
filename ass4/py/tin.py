import numpy as np
import rasterio
from .io import write_ras
from startinpy import DT


class TIN:
    def __init__(self, points):
        self.points = points
        self.dt = DT()
        self.dt.insert(points)

    def _laplace_interpolate(self, p):
        if not self.dt.is_inside_convex_hull(p[0], p[1]):
            return np.nan

        # tri = self.dt.locate(p)
        # p0, p1, p2 = self.dt.points[tri[0]], self.dt.points[tri[1]], self.dt.points[tri[2]]
        # TODO: fix later
        return self.dt.interpolate({"method": "Laplace"}, [[p[0], p[1]]])

    def to_gridded_points(self, cell_size):
        bbox = self.dt.get_bbox()
        rows = []
        for y in range(bbox[1], bbox[4], cell_size):
            cols = []
            if y > bbox[4]:
                break
            for x in range(bbox[0], bbox[3], cell_size):
                if x > bbox[3]:
                    break
                z = self._laplace_interpolate([x, y])
                cols.append([x + (cell_size / 2), y + (cell_size / 2), z])
            rows.append(cols)
        return rows

    def write_dtm(self, file_path):
        grid_points = np.array(self.to_gridded_points(0.5))
        # TODO: change profile later
        profile = {
            "driver": "GTiff",
            "dtype": "float32",
            "nodata": 0,
            "width": 100,
            "height": 100,
            "count": 1,
            "crs": "EPSG:32632",
            "transform": rasterio.transform.from_origin(  # type: ignore
                grid_points[0][0][0],
                grid_points[0][0][1],
                0.5,
                0.5,
            ),
        }

        write_ras(file_path, profile, grid_points[2])
