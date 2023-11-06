import geopandas as gpd
from shapely.ops import Point, MultiPoint, LineString, MultiLineString, GeometryCollection
from shapely import unary_union

from os.path import join

from src.env import SHP_PATH


class Walker:
    """Point over the path"""

    def __init__(
            self,
            previous: 'Walker' = None,
            next: list = None,  # list of Walkers
            current_pos: Point = None,
            target: Point = None,
            obstacles: list = None,  # list of Points
            path: MultiLineString = None,
            step_size: float = 1.0,
            reach_dist: float = 1.0
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

        self.is_path_end = False
        self.target_found = False

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
            next_steps = []
            for p in list(inter.geoms):
                if isinstance(p, Point):
                    if not self._matches_previous(p):
                        next_steps.append(p)

        # if there are next steps, the path updates to not include the previous walked sections
        path = self.path.difference(circle) if next_steps != [] else self.path

        # return remaining intersections
        return [
            Walker(
                previous=self,
                current_pos=ns,
                target=self.target,
                obstacles=self.obstacles,
                path=path,
                step_size=self.step_size,
                reach_dist=self.reach_dist
            ) for ns in next_steps
        ]

    def _walk(self):
        """
        Walks recursively the path
        :return: List containing if target was found (bool), and a list of visited Points
        """
        # base case: if dist(current_pos, target) < reach_dist, end here (path found)
        if self.current_pos.distance(self.target) <= self.reach_dist:
            self.is_path_end = True
            self.target_found = True
            return [self.target_found, [self.current_pos]]

        # base case: if dist(current_pos, obstacle) < step_size, end here (path blocked)
        for obstacle in self.obstacles:
            if self.current_pos.distance(obstacle) <= self.step_size:
                print(f'obstacle at {self}')
                self.is_path_end = True
                self.target_found = False
                return [self.target_found, [self.current_pos]]

        # find next step(s)
        self.next = self._find_next_steps()

        # base case: if there are no next steps, end here (dead end)
        if self.next == []:
            print(f'dead end at {self}')
            self.is_path_end = False
            self.target_found = False
            return [self.target_found, [self.current_pos]]

        # call walk() for every next Walker
        for w in self.next:
            [tf, pos_list] = w._walk()
            if tf:
                return [True, [self.current_pos] + pos_list]

        return [False, []]

    def walk(self):
        """
        Finds the path to the target Point
        :return: List of Points if path found, None otherwise
        """
        [tf, pos_list] = self._walk()
        if tf:
            return pos_list

        return None

    def __str__(self):
        return f"Walker({self.current_pos.x}, {self.current_pos.y})"


def _tests():
    lines = [
        LineString([(0, 0), (10, 0)]),
        LineString([(10, -1), (10, 11)]),
        LineString([(11, 10), (0, 10)]),
        LineString([(5, -1), (5, 11)]),
    ]
    starting_point = Point(2, 0)
    target_point = Point(0, 10)
    obstacles = [Point(5, 5)]

    path = unary_union(lines)

    w = Walker(
        current_pos=starting_point,
        target=target_point,
        obstacles=obstacles,
        path=path,
        step_size=0.153,
        reach_dist=0.153
    )
    # for ns in w._find_next_steps():
    #     print(ns)
    walk = w.walk()
    if walk is not None:
        for p in walk:
            print(p)

        lines_gdf = gpd.GeoDataFrame({'geometry': lines}, crs="EPSG:4326")
        sp_gdf = gpd.GeoDataFrame({'geometry': [starting_point]})
        tp_gdf = gpd.GeoDataFrame({'geometry': [target_point]})
        o_gdf = gpd.GeoDataFrame({'geometry': obstacles})
        walk_gdf = gpd.GeoDataFrame({'geometry': walk})

        lines_gdf.to_file(join(SHP_PATH, 'lines.shp'))
        sp_gdf.to_file(join(SHP_PATH, 'start.shp'))
        tp_gdf.to_file(join(SHP_PATH, 'target.shp'))
        o_gdf.to_file(join(SHP_PATH, 'obstacles.shp'))
        walk_gdf.to_file(join(SHP_PATH, 'walk.shp'))
    else:
        print('no hay camino')

    print("\033[32m _tests executed successfully \033[0m")


if __name__ == '__main__':
    print('\033[93m path_finder.py executed directly\n \033[0m')
    _tests()
