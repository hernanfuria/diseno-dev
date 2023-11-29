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


class _SegmentWalker:
    """"""

    def __init__(
            self, 
            total_path: list[LineString], 
            walked_path: list[LineString], 
            walked_points: list[Point],
            current_pos: Point,
            targets: list[Point],
            target_found: bool = False,
            tolerance: float | int = 0.1,
            forbidden_path: list[LineString] = []
    ) -> None:
        self._total_path = total_path
        self._walked_path = walked_path
        self._walked_points = walked_points
        self._current_pos = current_pos
        self._targets = targets
        self._target_found = target_found
        self._tolerance = tolerance
        self._forbidden_path = forbidden_path

    def get_target_found(self) -> bool:
        return self._target_found

    def get_walked_path(self) -> list:
        return self._walked_path
    
    def get_walked_points(self) -> list:
        return self._walked_points

    def set_forbidden_path(self, forbidden_path: list[LineString]) -> None:
        self._forbidden_path = forbidden_path

    def _remove_redundant_points(self, points: list[Point]) -> list[Point]:
        redundant_idx = []
        for p_idx in range(1, len(points) - 1):
            p_prev: Point = points[p_idx - 1]
            p_curr: Point = points[p_idx]
            p_next: Point = points[p_idx + 1]

            v1 = (p_curr.x - p_prev.x, p_curr.y - p_prev.y)  # p_prev to p_curr
            v2 = (p_next.x - p_curr.x, p_next.y - p_curr.y)  # p_curr to p_next
            v2_90 = (v2[1], -1 * v2[0])  # v2 rotated 90 degrees

            m1 = ((v1[0] ** 2) + (v1[1] ** 2)) ** 0.5
            m2 = ((v2[0] ** 2) + (v2[1] ** 2)) ** 0.5

            versor1 = (v1[0] / m1, v1[1] / m1)
            versor2_90 = (v2_90[0] / m2, v2_90[1] / m2)

            scalar_prod = versor1[0] * versor2_90[0] + versor1[1] * versor2_90[1]

            # v1 // v2 <=> v1 perp v2_90 <=> v1 . v2_90 == 0
            if abs(scalar_prod) < 0.01:
                redundant_idx.append(p_idx)

        clean_points = []
        for p_idx, p in enumerate(points):
            if p_idx not in redundant_idx:
                clean_points.append(p)

        return clean_points

    def get_clean_path(self) -> LineString:
        return LineString(
            self._remove_redundant_points(
                points=self.get_walked_points()
            )
        )

    def _get_opposite_end(self, line: LineString) -> Point | None:
        """
        If self._current_pos matches an end of the parameter line, 
        returns the other end. Returns None otherwise.
        """

        if self._current_pos.distance(Point(line.coords[0])) <= self._tolerance:
            return Point(line.coords[-1])
        
        if self._current_pos.distance(Point(line.coords[-1])) <= self._tolerance:
            return Point(line.coords[0])
        
        return None

    def _check_target_found(self) -> None:
        """
        Checks if the current position matches a target and 
        updates self.target_found
        """

        for target in self._targets:
            if self._current_pos.distance(target) <= self._tolerance:
                if target not in self._walked_points:
                    self._walked_points.append(target)
                self._target_found = True
                return
            
        self._target_found = False
        
    def get_next_walkers(self) -> list:
        """
        Returns a list of the next walkers with the accumulated walked path.
        If the path can continue, the list contains 1 or more walkers.
        If a target was found, the returned list contains the current walker.
        If there is no next walkers (dead end), an empty list is returned.
        """

        if not self._target_found:
            self._check_target_found()
        if self._target_found:
            return [self]

        next_walkers = []
        for line in self._total_path:
            if line not in self._walked_path + self._forbidden_path:
                opposite_end = self._get_opposite_end(line)
                if opposite_end is not None:
                    next_walkers.append(
                        _SegmentWalker(
                            total_path=self._total_path,
                            walked_path=self._walked_path + [line],
                            walked_points=self._walked_points + [self._current_pos],
                            current_pos=opposite_end,
                            targets=self._targets,
                            target_found=False,
                            tolerance=self._tolerance
                        )
                    )
        
        return next_walkers
    
    def __str__(self) -> str:
        x = round(self._current_pos.x, 5)
        y = round(self._current_pos.y, 5)

        if self.get_target_found():
            return green(f"SW({x}, {y}, wpl={len(self._walked_path)})")
        
        return magenta(f"SW({x}, {y}, wpl={len(self._walked_path)})")
    
class _Walk:
    """"""

    def __init__(
            self,
            source: Point,
            path: list[LineString],
            targets: list[Point],
            tolerance: float | int = 0.1
    ) -> None:
        self._source = source
        self._path = path
        self._targets = targets
        self._tolerance = tolerance

    def _path_can_be_walked(self, walkers: list[_SegmentWalker]) -> bool:
        """Returns True if there are walkers which have not reached a target."""

        for walker in walkers:
            if not walker.get_target_found():
                return True
        
        return False

    def _report_walkers(self, walkers: list[_SegmentWalker], iteration: int) -> None:
        print(f"Iteration: {iteration}")
        for walker in walkers:
            print(walker)
        print(' ')

    def walk(self) -> list[LineString]:
        """Manages _SegmentWalker(s) to find all posible paths to targets"""

        walkers = [
            _SegmentWalker(  # source walker
                total_path=self._path,
                walked_path=[],
                walked_points=[],
                current_pos=self._source,
                targets=self._targets,
                target_found=False,
                tolerance=self._tolerance
            )
        ]

        iteration = 0
        while self._path_can_be_walked(walkers):
            iteration += 1
            self._report_walkers(walkers, iteration)

            # find next walkers
            old_walkers = [walker for walker in walkers]
            walkers = []
            for old_walker in old_walkers:
                walkers += old_walker.get_next_walkers()

            # share walked path so no path is walked more than once
            forbidden_path = []
            for walker in walkers:
                walker: _SegmentWalker
                forbidden_path += walker.get_walked_path()
            for walker in walkers:
                walker.set_forbidden_path(forbidden_path)

        self._report_walkers(walkers, -1)

        return [walker.get_clean_path() for walker in walkers]



