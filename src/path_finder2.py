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


class _SegmentWalker:
    """"""

    def __init__(
            self, 
            total_path: list[LineString], 
            walked_path: list[LineString], 
            current_pos: Point,
            tolerance: float | int = 0.1
    ) -> None:
        self._total_path = total_path
        self._walked_path = walked_path
        self._current_pos = current_pos
        self.tolerance = tolerance

    def _get_opposite_end(self, line: LineString) -> Point | None:
        """
        If self._current_pos matches an end of the parameter line, 
        returns the other end. Returns None otherwise.
        """

        if self._current_pos.distance(line.coords[0]) <= self.tolerance:
            return Point(line.coords[-1])
        
        if self._current_pos.distance(line.coords[-1]) <= self.tolerance:
            return Point(line.coords[0])
        
        return None

    def get_next_walkers(self) -> list:
        """
        Returns a list of the next walkers with the accumulated walked path.
        """

        next_walkers = []
        for line in self._total_path:
            if line not in self._walked_path:
                opposite_end = self._get_opposite_end(line)
                if opposite_end is not None:
                    next_walkers.append(
                        _SegmentWalker(
                            total_path=self._total_path,
                            walked_path=self._walked_path + line,
                            current_pos=opposite_end,
                            tolerance=self.tolerance
                        )
                    )
        
        return next_walkers
