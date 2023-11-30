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


class FATGraphGrouperThread:  # (QThread):
    """Thread in charge of grouping all FATs"""

    def __init__(
            self,
            fat_graph: FATGraph,
            n: int
    ) -> None:
        self._fat_graph = fat_graph
        self._n = n

    def run(self) -> list[dict]:
        return self.group_by_n()

    def group_by_n(self) -> list[dict]:
        return self._fat_graph.group_by_n(
            n=self._n,
            evaluate_data_key='weight',
            retrieve_data_key='linestring'
        )