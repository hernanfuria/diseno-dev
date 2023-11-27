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
            targets: list[Point],
            target_found: bool = False,
            tolerance: float | int = 0.1
    ) -> None:
        self._total_path = total_path
        self._walked_path = walked_path
        self._current_pos = current_pos
        self._targets = targets
        self._target_found = target_found
        self._tolerance = tolerance

    def _get_opposite_end(self, line: LineString) -> Point | None:
        """
        If self._current_pos matches an end of the parameter line, 
        returns the other end. Returns None otherwise.
        """

        if self._current_pos.distance(line.coords[0]) <= self._tolerance:
            return Point(line.coords[-1])
        
        if self._current_pos.distance(line.coords[-1]) <= self._tolerance:
            return Point(line.coords[0])
        
        return None

    def _check_target_found(self) -> None:
        """
        Checks if the current position matches a target and 
        updates self.target_found
        """

        for target in self._targets:
            if self._current_pos.distance(target) <= self._tolerance:
                self._target_found = True
                return
            
        self._target_found = False
        
    def get_next_walkers(self) -> list:
        """
        Returns a list of the next walkers with the accumulated walked path.
        """

        if not self._target_found:
            self._check_target_found()
        if self._target_found:
            return []

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
                            targets=self._targets,
                            target_found=False,
                            tolerance=self._tolerance
                        )
                    )
        
        return next_walkers
