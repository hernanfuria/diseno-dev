import geopandas as gpd
from shapely.ops import (
    Point,
    MultiPoint,
    LineString,
    MultiLineString,
    GeometryCollection,
    nearest_points
)
from shapely import unary_union, intersection

from os.path import join

from src.env import SHP_PATH
from src.path_finder2 import _SegmentWalker, _Walk, path_finder
from src.main_thread import MainThread
from src.clic import red, green, orange


def _test1():
    mt = MainThread()
    mt.run()

    print(green("_test1 executed successfully"))


def _tests():
    _test1()


if __name__ == '__main__':
    print(orange("main_thread_tests.py executed directly\n"))
    _tests()