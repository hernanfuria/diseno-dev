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
from src.clic import red, green, orange


class MainThread:
    """This class in only meant for simulating the main thread"""

    def __init__(self) -> None:
        pass

    def run(self):
        print(green('RUNNING MAIN THREAD'))

        # read data
        fats_gdf = gpd.read_file(join(SHP_PATH, 'NAPs.shp'))
        path_gdf = gpd.read_file(join(SHP_PATH, 'Strands.shp'))
        print(green('shps read'))

        path = list(path_gdf.geometry)

        path_ends = []
        for p_idx, p in enumerate(path):
            print(f"\tcollecting line ends ( {p_idx + 1} / {len(path)} \t|\t{int((p_idx + 1) * 100 / len(path))} % )")
            p1 = Point(p.coords[0])
            p2 = Point(p.coords[-1])
            if p1 not in path_ends:
                path_ends.append(p1)
            if p2 not in path_ends:
                path_ends.append(p2)
        path_ends = unary_union(path_ends)

        print("\tsnapping")
        for i in range(fats_gdf.index.size):
            fats_gdf.loc[i, 'geometry'] = nearest_points(path_ends, fats_gdf.loc[i, 'geometry'])[0]


        print(green('geometries collected'))

        # find/collect paths
        all_paths = []
        for i in range(fats_gdf.index.size): 
            s_name = fats_gdf.loc[i, 'Numero_NAP']
            print(f"\tfinding paths from {s_name} ( {i + 1} / {fats_gdf.index.size} \t|\t{(i + 1) * 100 / fats_gdf.index.size} % )")
            source = fats_gdf.loc[i, 'geometry']
            # source = list(fats_gdf[fats_gdf['Numero_NAP'] == s_name]['geometry'])[0]
            targets = list(fats_gdf[fats_gdf['Numero_NAP'] != s_name]['geometry'])
            meter = 0.00001
            paths_found = path_finder(
                source=source,
                path=path,
                targets=targets,
                tolerance=meter * 0.5
            )
            print(f"{paths_found}\n")

            all_paths += paths_found
            all_paths_gdf = gpd.GeoDataFrame({'geometry': all_paths}, crs=4326)
            all_paths_gdf.to_file(join(SHP_PATH, 'MainThreadTest.shp'))

        print(green('walk ended'))

        # create/collect graph
        # find groups by n
        pass