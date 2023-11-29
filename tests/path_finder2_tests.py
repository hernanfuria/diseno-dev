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
from src.path_finder2 import _SegmentWalker, _Walk
from src.clic import red, green, orange


def _test1():
    # read shps
    fats_gdf = gpd.read_file(join(SHP_PATH, 'NAPs.shp'))
    path_gdf = gpd.read_file(join(SHP_PATH, 'Strands.shp'))
    print(green('shps read'))

    # select geometries
    path = list(path_gdf.geometry)

    path_ends = []
    for p_idx, p in enumerate(path):
        print(f"\tcollecting line ends ( {p_idx + 1} / {len(path)} )")
        p1 = Point(p.coords[0])
        p2 = Point(p.coords[-1])
        if p1 not in path_ends:
            path_ends.append(p1)
        if p2 not in path_ends:
            path_ends.append(p2)
    path_ends = unary_union(path_ends)

    print("\tsnapping")
    s_name = 'F103'
    s = list(fats_gdf[fats_gdf['Numero_NAP'] == s_name]['geometry'])[0]
    t_list = list(fats_gdf[fats_gdf['Numero_NAP'] != s_name]['geometry'])

    source = nearest_points(path_ends, s)[0]
    targets = []
    for t_idx, t in enumerate(t_list):
        print(f"\tsnapping ( {t_idx + 1} / {len(t_list)} )")
        targets.append(nearest_points(path_ends, t)[0])

    print(green('geometries extracted'))

    # find paths
    meter = 0.00001
    w = _Walk(
        source=source,
        path=path,
        targets=targets,
        tolerance=meter * 0.5
    )
    paths_found = w.walk()
    print(green('walk ended'))

    # export paths found to shp
    # segments_walk_geometries = []
    # for pf in paths_found:
    #     segments_walk_geometries.append(unary_union(pf))

    # path_points = []
    # for pf in paths_found:
    #     path_points += pf
    sw_gdf = gpd.GeoDataFrame({'geometry': paths_found}, crs=4326)
    sw_gdf.to_file(join(SHP_PATH, 'SegmentsWalk.shp'))
    print(green('shp saved'))

    print(green("_test1 executed successfully"))


def _tests():
    _test1()

if __name__ == '__main__':
    print(orange("path_finder2_tests.py executed directly\n"))
    _tests()