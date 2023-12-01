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
from src.fat_graph import FATGraph
from src.fat_graph_constructor_thread import FATGraphConstructorThread
from src.path_finder_thread import PathFinderThread
from src.fat_graph_grouper_thread import FATGraphGrouperThread
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
        find_paths = False

        meter = 0.00001
        if find_paths:
            all_paths = []
            for i in range(fats_gdf.index.size): 
                try:
                    pft = PathFinderThread(
                        source_fat_gdf=fats_gdf,
                        source_fat_id_col='Numero_NAP',
                        source_fat_idx=i,
                        path=path,
                        tolerance=meter * 0.5
                    )
                    paths_found = pft.run()

                    print(f"{paths_found}\n")

                    all_paths += paths_found
                    all_paths_gdf = gpd.GeoDataFrame({'geometry': all_paths}, crs=4326)
                    all_paths_gdf.to_file(join(SHP_PATH, 'all_paths.shp'))
                except Exception:
                    print(red(f"ERROR IN FAT {i}\n"))
                    try:
                        with open(join(SHP_PATH, 'log.txt'), 'a') as log_file:
                            log_file.write(f"ERROR IN FAT {i}\n")
                        continue
                    except Exception:
                        continue
            print(green('walk ended'))
        else:
            all_paths_gdf = gpd.read_file(join(SHP_PATH, 'all_paths.shp'))
            print(green('paths read'))

        

        # create/collect graph
        fatgct = FATGraphConstructorThread(
            fats_gdf=fats_gdf,
            fats_id_column='Numero_NAP',
            all_paths_gdf=all_paths_gdf,
            tolerance=meter * 0.1
        )
        fat_graph = fatgct.run()
        print(fat_graph)
        print(green('graph constructed'))


        # find groups by n
        fatggt = FATGraphGrouperThread(
            fat_graph=fat_graph,
            n=16
        )
        groups = fatggt.run()

        groups_dict = {
            'group': [],
            'geometry': []
        }
        for group_idx, group in enumerate(groups):
            for line in group['edges_in_group']:
                groups_dict['group'].append(group_idx)
                groups_dict['geometry'].append(line)
        group_paths_gdf = gpd.GeoDataFrame(groups_dict, crs=4326)
        group_paths_gdf.to_file(join(SHP_PATH, 'group_paths.shp'))

        print(green('groups done'))