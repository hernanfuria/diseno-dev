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

from src.env import SHP_PATH
from src.clic import red, green, orange
from src.logger import Logger


class _Walker:
    """Point over the path"""

    def __init__(
            self,
            previous: '_Walker' = None,
            next: list = None,  # list of Walkers
            current_pos: Point = None,
            target: Point = None,
            obstacles: list = None,  # list of Points
            path: MultiLineString = None,
            step_size: float = 1.0,
            reach_dist: float = 1.0,
            max_walking_distance: float = 10.0
    ):
        """
        :param previous: Previous Walker to the one being instatiated
        :param next: List of Walker objects that are found after this one
        :param current_pos: shapely Point object, current position of this Walker object
        :param target: shapely Point object, The location where the walker is trying to reach
        :param obstacles: List of shapely Point objects, obstacles in the path (not implemented yet)
        :param path: shapely LineString or MultiLineString object, the path the Walker walks
        :param step_size: Distance between a Walker object and its next one(s)
        :param reach_dist: Maximum distance from the target at which the Walker is considered arrived
        :param max_walking_distance: Maximum distance the Walker is able to walk
        """

        # input checks
        if not isinstance(current_pos, Point):
            raise ValueError(f"current_pos: {current_pos} is not a Point object")
        if not isinstance(target, Point):
            raise ValueError(f"target: {target} is not a Point object")
        if not (isinstance(path, MultiLineString) or isinstance(path, LineString)):
            raise ValueError(f"path: {path} is not a MultiLineString or LineString object")

        self.previous = previous
        self.next = next if next is not None else []
        self.current_pos = current_pos
        self.target = target
        self.obstacles = obstacles if obstacles is not None else []
        self.path = path
        self.step_size = step_size
        self.reach_dist = reach_dist
        self.max_walking_distance = max_walking_distance

        self.l = Logger(log_type='cli')

    def get_pos(self):
        """Returns the current position of the Walker"""
        return self.current_pos

    def _matches_previous(self, p: Point) -> bool:
        """

        :param p: Some Point
        :return: True if a Point matches the previous Walker's position, False otherwise
        """

        if self.previous is None:
            return False
        return p.distance(self.previous.get_pos()) < (self.reach_dist / 100)

    def _remove_redundant_points(self, pos_list: list) -> list:
        redundant_idx = []
        for p_idx in range(1, len(pos_list) - 1):
            p_prev: Point = pos_list[p_idx - 1]
            p_curr: Point = pos_list[p_idx]
            p_next: Point = pos_list[p_idx + 1]

            v1 = (p_curr.x - p_prev.x, p_curr.y - p_prev.y)  # p_prev to p_curr
            v2 = (p_next.x - p_curr.x, p_next.y - p_curr.y)  # p_curr to p_next
            v2_90 = (v2[1], -1 * v2[0])  # v2 rotated 90 degrees

            scalar_prod = v1[0] * v2_90[0] + v1[1] * v2_90[1]

            # v1 // v2 <=> v1 perp v2 <=> v1 . v2_90 == 0
            if scalar_prod == 0:
                redundant_idx.append(p_idx)

        clean_pos_list = []
        for p_idx, p in enumerate(pos_list):
            if p_idx not in redundant_idx:
                clean_pos_list.append(p)

        return clean_pos_list

    def _sort_next_steps(self, unsorted_next_steps: list) -> list:
        """"""

        if len(unsorted_next_steps) == 1:
            return unsorted_next_steps

        scalar_products = []

        # current pos to target versor
        ct_versor_x = self.target.x - self.current_pos.x
        ct_versor_y = self.target.y - self.current_pos.y
        ct_versor_mod = ((ct_versor_x ** 2) + (ct_versor_y ** 2)) ** 0.5
        ct_versor = (ct_versor_x / ct_versor_mod, ct_versor_y, ct_versor_mod)

        for uns in unsorted_next_steps:
            # current pos to unsorted next step versor
            cuns_versor_x = uns.x - self.current_pos.x
            cuns_versor_y = uns.y - self.current_pos.y
            cuns_versor_mod = ((cuns_versor_x ** 2) + (cuns_versor_y ** 2)) ** 0.5
            cuns_versor = (cuns_versor_x / cuns_versor_mod, cuns_versor_y, cuns_versor_mod)

            scalar_product = (ct_versor[0] * cuns_versor[0]) + (ct_versor[1] * cuns_versor[1])
            scalar_products.append(scalar_product)

        sorted_scalar_products = [sc for sc in scalar_products]
        sorted_scalar_products.sort()

        sorted_indexes = []
        for ssp in sorted_scalar_products:
            for sp_idx, sp in enumerate(scalar_products):
                if sp == ssp and sp_idx not in sorted_indexes:
                    sorted_indexes.append(sp_idx)

        sorted_next_steps = []
        for i in sorted_indexes:
            sorted_next_steps.append(unsorted_next_steps[i])
        return sorted_next_steps

    def _find_next_steps(self) -> list:
        """
        :return: List of next Walker objects
        """

        # create a ring buffer of current_pos with radius step_size
        circle = self.current_pos.buffer(self.step_size)
        ring = circle.boundary

        # find intersections between path and ring
        inter = ring.intersection(self.path)

        # search the previous Walker inside intersections and delete it
        next_steps = []
        if isinstance(inter, Point):
            if not self._matches_previous(inter):
                next_steps = [inter]
        if isinstance(inter, MultiPoint) or isinstance(inter, GeometryCollection):
            unsorted_next_steps = []
            for p in list(inter.geoms):
                if isinstance(p, Point):
                    if not self._matches_previous(p):
                        unsorted_next_steps.append(p)
            next_steps = self._sort_next_steps(unsorted_next_steps)

        # if there are next steps, the path updates to not include the previous walked sections
        path = self.path.difference(circle) if next_steps != [] else self.path

        # return remaining intersections
        return [
            _Walker(
                previous=self,
                current_pos=ns,
                target=self.target,
                obstacles=self.obstacles,
                path=path,
                step_size=self.step_size,
                reach_dist=self.reach_dist,
                max_walking_distance=self.max_walking_distance - self.step_size
            ) for ns in next_steps
        ]

    def _base_case_path_found(self) -> bool:
        """
        If the target is closer that reach_dist to the _Walker, 
        the path has been found
        """

        # base case: if dist(current_pos, target) <= reach_dist, end here (path found)
        return self.current_pos.distance(self.target) <= self.reach_dist

    def _base_case_path_blocked(self) -> bool:
        """
        If an obstacle is closer that step_size to the _Walker, 
        the path is blocked
        """

        # base case: if dist(current_pos, obstacle) < step_size, end here (path blocked)
        for obstacle in self.obstacles:
            if self.current_pos.distance(obstacle) <= self.step_size:
                return True
            
    def _base_case_max_distance_walked(self) -> bool:
        """
        If max_walking_distance is smaller that step_size, 
        the _Walker can't move because the maximum walking 
        distance has been walked
        """

        # base case: if max_walking_distance < step_size, end here (max distance walked)
        return self.max_walking_distance < self.step_size
    
    def _base_case_dead_end(self) -> bool:
        """
        If there are no next _Walkers, the current _Walker 
        has reached a dead end
        """
        
        # base case: if there are no next steps, end here (dead end)
        return self.next == []

    def _walk(self) -> list:
        """
        Walks recursively the path
        :return: List containing if target was found (bool), 
            a list of visited Points, and an updated path
        """
        if self._base_case_path_found():
            self._log(green(f"Target found at {self}"))
            return [True, [self.current_pos], self.path]

        if self._base_case_path_blocked():
            self._log(red(f"Obstacle found at {self}"))
            return [False, [], self.path]

        if self._base_case_max_distance_walked():
            self._log(red(f"Max distance walked at {self}"))
            return [False, [], self.path]

        # find next step(s)
        self.next = self._find_next_steps()

        if self._base_case_dead_end():
            self._log(red(f"Dead end at {self}"))
            return [False, [], self.path]

        # self.l.log(light_gray(f"Walking at {self}"))

        # call _walk() for every next Walker
        path = None
        for w in self.next:
            if path is not None:
                w.path = path

            [tf, pos_list, path] = w._walk()

            if tf:
                return [True, [self.current_pos] + pos_list, self.path]

        return [False, [], path]

    def walk(self) -> LineString:
        """
        Finds the path to the target Point
        :return: List of Points if path found, None otherwise
        """
        [tf, pos_list, path] = self._walk()
        if tf:
            pos_list.append(self.target)
            return LineString(self._remove_redundant_points(pos_list))

        return None

    def _log(self, log: str) -> None:
        """Handles the log"""
        
        self.l.log(log)

    def __str__(self):
        return f"({self.current_pos.x}, {self.current_pos.y})"


def path_finder(
        source: Point, 
        target: Point, 
        path: MultiLineString, 
        obstacles: list = None,
        step_size: float = 1,
        max_walking_distance: float = 100
):
    """
    Tries to find the path from source point to target point, 
    wandering through the path.
    """

    w = _Walker(
        current_pos=source,
        target=target,
        obstacles=obstacles,
        path=path,
        step_size=step_size,
        reach_dist=step_size,
        max_walking_distance=max_walking_distance
    )

    return w.walk()


if __name__ == '__main__':
    print(orange('path_finder.py executed directly'))
