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
from src.path_finder import _Walker, path_finder
from src.clic import red, green, orange


def _test1():
    lines = [
        LineString([(0, 0), (20, 0)]),
        LineString([(10, -10), (10, 20)]),
        LineString([(20, 10), (0, 10)]),
        LineString([(5, -10), (5, 20)]),
    ]
    starting_point = Point(2, 0)
    target_point = Point(0, 10)
    obstacles = [
        Point(5, 5),
        # Point(10, 5),
        Point(15, 0),
        Point(5, -5),
        Point(10, -5),
    ]

    path = unary_union(lines)

    w = _Walker(
        current_pos=starting_point,
        target=target_point,
        obstacles=obstacles,
        path=path,
        step_size=0.153,
        reach_dist=0.153,
        max_walking_distance=100
    )

    lines_gdf = gpd.GeoDataFrame({'geometry': lines}, crs="EPSG:4326")
    sp_gdf = gpd.GeoDataFrame({'geometry': [starting_point]})
    tp_gdf = gpd.GeoDataFrame({'geometry': [target_point]})
    o_gdf = gpd.GeoDataFrame({'geometry': obstacles})

    lines_gdf.to_file(join(SHP_PATH, 'lines.shp'))
    sp_gdf.to_file(join(SHP_PATH, 'start.shp'))
    tp_gdf.to_file(join(SHP_PATH, 'target.shp'))
    o_gdf.to_file(join(SHP_PATH, 'obstacles.shp'))

    walk = w.walk()
    if walk is not None:
        print(walk)
        walk_gdf = gpd.GeoDataFrame({'geometry': [walk]})
        walk_gdf.to_file(join(SHP_PATH, 'walk.shp'))
    else:
        print('no hay camino')

    print(green("_test1 executed successfully"))


def _test2():
    strands_gdf = gpd.read_file(join(SHP_PATH, 'Strands.shp'))
    start_gdf = gpd.read_file(join(SHP_PATH, 'ComplexStart.shp'))
    target_gdf = gpd.read_file(join(SHP_PATH, 'ComplexTarget.shp'))
    print(green("layers read"))

    meter = 0.00001

    w = _Walker(
        current_pos=start_gdf.loc[0, 'geometry'],
        target=target_gdf.loc[0, 'geometry'],
        obstacles=[],
        path=unary_union(list(strands_gdf.geometry)),
        step_size=1 * meter,
        reach_dist=1 * meter,
        max_walking_distance=400 * meter
    )

    walk = w.walk()
    if walk is not None:
        print(walk)
        walk_gdf = gpd.GeoDataFrame({'geometry': [walk]})
        walk_gdf.to_file(join(SHP_PATH, 'ComplexWalk.shp'))
        print(green("\tComplexWalk.shp saved"))
    else:
        print(red('no hay camino'))

    print(green("_test2 executed successfully"))


def _test3():
    naps_gdf = gpd.read_file(join(SHP_PATH, 'NAPs.shp'))
    strands_gdf = gpd.read_file(join(SHP_PATH, 'Strands.shp'))

    path = unary_union(list(strands_gdf.geometry))  # MultiLineString
    naps = [nearest_points(nap, path)[1] for nap in list(naps_gdf.geometry)]  # list of Points

    # test
    test_gdf = gpd.GeoDataFrame({'geometry': naps})
    test_gdf.to_file(join(SHP_PATH, 'test.shp'))

    nap_to_nap_max_dist = 500
    meter = 0.00001

    paths_found = []
    for s_idx, s in enumerate(naps):  # starting NAP
        for e_idx, e in enumerate(naps):  # end NAP
            if s_idx < e_idx and s.distance(e) < nap_to_nap_max_dist * meter:
                print(f"s: {s_idx} of {len(naps)}, e: {e_idx} of {len(naps)}")

                obstacles = [n for n_idx, n in enumerate(naps) if n_idx not in [s_idx, e_idx]]
                near_path = intersection(path, s.buffer(nap_to_nap_max_dist * meter))

                w = _Walker(
                    current_pos=s,
                    target=e,
                    obstacles=obstacles,
                    path=near_path,
                    step_size=3 * meter,
                    reach_dist=3 * meter,
                    max_walking_distance=nap_to_nap_max_dist * meter
                )

                walk = w.walk()
                if walk is not None:
                    # print(walk)
                    print(green("\tpath found"))
                    paths_found.append(walk)

                else:
                    print(red('\tno path'))

    if paths_found != []:
        walk_gdf = gpd.GeoDataFrame({'geometry': paths_found})
        walk_gdf.to_file(join(SHP_PATH, 'ComplexWalk.shp'))
        print(green("\tComplexWalk.shp saved"))
    else:
        print(red('\tno hay ningun camino'))

    print(green("_test3 executed successfully"))


def _tests():
    _test3()

if __name__ == '__main__':
    print(orange("path_finder.tests.py executed directly\n"))
    _tests()
