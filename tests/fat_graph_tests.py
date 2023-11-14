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
from src.fat_graph import FATGraph
from src.clic import red, green, orange


def _test1():
    fatg = FATGraph(
        fats=['f1', 'f2', 'f3', 'f4', 'f5'],
        edges=[
            (
                'f1', 
                'f2',
                {'weight': 3}
            ),
            (
                'f2', 
                'f4',
                {'weight': 6}
            ),
            (
                'f3', 
                'f5',
                {'weight': 1}
            ),
        ]
    )
    print(fatg)
    print(green("_test1 executed successfully"))

def _test2():

    # N 3 N 2 1
    # 3 N 6 1 2
    # N 6 N 1 N
    # 2 1 1 N 8
    # 1 2 N 8 N

    fatg = FATGraph(
        fats=['f1', 'f2', 'f3', 'f4', 'f5'],
        edges=[
            ('f1', 'f2', {'weight': 3}),
            ('f1', 'f4', {'weight': 2}),
            # ('f1', 'f5', {'weight': 1}),
            ('f2', 'f3', {'weight': 6}),
            ('f2', 'f4', {'weight': 1}),
            ('f2', 'f5', {'weight': 2}),
            ('f3', 'f4', {'weight': 1}),
            ('f4', 'f5', {'weight': 8})
        ]
    )
    print(fatg)
    print(fatg._get_most_disconnected_fat(evaluate_data_key='weight'))

    print(green("_test2 executed successfully"))

def _test3():

    # N 3 N 2 1
    # 3 N 6 1 2
    # N 6 N 1 N
    # 2 1 1 N 8
    # 1 2 N 8 N

    fatg = FATGraph(
        fats=['f1', 'f2', 'f3', 'f4', 'f5'],
        edges=[
            ('f1', 'f2', {'weight': 3}),
            ('f1', 'f4', {'weight': 2}),
            ('f1', 'f5', {'weight': 1}),
            ('f2', 'f3', {'weight': 6}),
            ('f2', 'f4', {'weight': 1}),
            ('f2', 'f5', {'weight': 2}),
            ('f3', 'f4', {'weight': 1}),
            ('f4', 'f5', {'weight': 8})
        ]
    )
    print(fatg)
    print(fatg._get_most_disconnected_fat(evaluate_data_key='weight'))
    print(fatg._create_group(3, 'weight', 'weight'))

    print(green("_test3 executed successfully"))

def _test4():

    # N 3 N 2 1
    # 3 N 6 1 2
    # N 6 N 1 N
    # 2 1 1 N 8
    # 1 2 N 8 N

    fatg = FATGraph(
        fats=['f1', 'f2', 'f3', 'f4', 'f5'],
        edges=[
            ('f1', 'f2', {'weight': 3}),
            ('f1', 'f4', {'weight': 2}),
            ('f1', 'f5', {'weight': 1}),
            ('f2', 'f3', {'weight': 6}),
            ('f2', 'f4', {'weight': 1}),
            ('f2', 'f5', {'weight': 2}),
            ('f3', 'f4', {'weight': 1}),
            ('f4', 'f5', {'weight': 8})
        ]
    )
    print(fatg)
    print(fatg._get_most_disconnected_fat(evaluate_data_key='weight'))
    print(fatg.group_by_n(3, 'weight', 'weight'))

    print(green("_test4 executed successfully"))

def _test5():
    fats_gdf: gpd.GeoDataFrame = gpd.read_file(join(SHP_PATH, 'FATs (FATGraph testing).shp'))
    lats_gdf: gpd.GeoDataFrame = gpd.read_file(join(SHP_PATH, 'Lat (FATGraph testing).shp'))

    fats = [fats_gdf.loc[i, 'Numero_FAT'] for i in range(fats_gdf.index.size)]
    edges = []

    for lat_idx, lat_row in lats_gdf.iterrows():
        print(f"Checking lat {lat_idx}")
        lat: LineString = lat_row['geometry']
        e = []
        for fat_idx, fat_row in fats_gdf.iterrows():
            print(f"\tChecking fat {fat_idx}")
            fat: Point = fat_row['geometry']
            fat_name: str = fat_row['Numero_FAT']
            if fat.distance(Point(lat.coords[0])) < 0.00001 * 0.1 or fat.distance(Point(lat.coords[-1])) < 0.00001 * 0.1:
                e.append(fat_name)
            if len(e) == 2:
                e.append({'weight': lat.length, 'linestring': lat})
                break
        edges.append(tuple(e))

    print(green(fats))
    for edge in edges:
        print(green(edge))

    fatg = FATGraph(fats=fats, edges=edges)
    output_lats = []
    groups = fatg.group_by_n(n=4, evaluate_data_key='weight', retrieve_data_key='linestring')
    for group in groups:
        edges_in_group = group['edges_in_group']
        for eig in edges_in_group:
            output_lats.append(eig)

    output_lats_gdf = gpd.GeoDataFrame({'geometry': output_lats}, crs=lats_gdf.crs)
    output_lats_gdf.to_file(join(SHP_PATH, 'GroupLat (FATGraph testing).shp'))

    print(green("_test5 executed successfully"))

def _tests():
    _test5()


if __name__ == "__main__":
    print(orange("fat_graph_tests.py executed directly\n"))
    _tests()