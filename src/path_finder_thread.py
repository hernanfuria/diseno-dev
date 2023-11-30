from __future__ import annotations

import geopandas as gpd
from shapely.ops import (
    Point,
    MultiPoint,
    LineString,
    MultiLineString,
    GeometryCollection,
    nearest_points
)
from shapely import unary_union

from os.path import join

from src.clic import red, green, orange, magenta
from src.fat_graph import FATGraph
from src.path_finder2 import path_finder


class PathFinderThread:  # (QThread):
    """Thread in charge of finding all paths from a source FAT"""

    def __init__(
            self,
            source_fat_gdf: gpd.GeoDataFrame,
            source_fat_id_col: str,
            source_fat_idx: int,
            path: list[LineString],
            tolerance: float | int = 0.1
    ) -> None:
        self._source_fat_gdf = source_fat_gdf
        self._source_fat_id_col = source_fat_id_col    
        self._source_fat_idx = source_fat_idx
        self._path = path
        self._tolerance = tolerance

    def run(self) -> list[LineString]:
        return self.find_paths()

    def find_paths(self) -> list[LineString]:
        s_name = self._source_fat_gdf.loc[self._source_fat_idx, self._source_fat_id_col]
        print(f"\tfinding paths from {s_name} ( {self._source_fat_idx + 1} / {self._source_fat_gdf.index.size} \
              \t|\t{(self._source_fat_idx + 1) * 100 / self._source_fat_gdf.index.size} % )")
        source = self._source_fat_gdf.loc[self._source_fat_idx, 'geometry']
        targets = list(self._source_fat_gdf[self._source_fat_gdf[self._source_fat_id_col] != s_name]['geometry'])
        
        return path_finder(
            source=source,
            path=self._path,
            targets=targets,
            tolerance=self._tolerance
        )
