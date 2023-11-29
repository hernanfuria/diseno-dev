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
from fat_graph import FATGraph
from path_finder2 import path_finder


class PathFinderThread:  # (QThread):
    """"""

    def __init__(self) -> None:
        pass

    def run(self):
        pass
