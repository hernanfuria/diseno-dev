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
from src.fat_graph import FATGraph
from src.path_finder2 import path_finder


class FATGraphConstructorThread:
    """Thread in charge of contructing the FATGraph"""

    def __init__(
            self, 
            fats_gdf: gpd.GeoDataFrame, 
            fats_id_column: str, 
            all_paths_gdf: gpd.GeoDataFrame,
            tolerance: float | int
    ) -> None:
        self.fats_gdf = fats_gdf
        self.fats_id_column = fats_id_column
        self.all_paths_gdf = all_paths_gdf

        self.tolerance = tolerance

        self.fat_graph = FATGraph(fats=list(self.fats_gdf[self.fats_id_column]))

    def run(self) -> FATGraph:
        return self.create_fat_graph()

    def _matches_line_end(
        self, 
        ends: tuple[int], 
        path: LineString, 
        fat1: str, 
        fat1_geom: Point, 
        i: int
    ):
        if Point(path.coords[ends[0]]).distance(fat1_geom) < self.tolerance:
            for j in range(self.fats_gdf.index.size): 
                if j != i:
                    fat2 = self.fats_gdf.loc[j, self.fats_id_column]
                    fat2_geom: Point = self.fats_gdf.loc[j, 'geometry']
                    if Point(path.coords[ends[1]]).distance(fat2_geom) < self.tolerance:
                        data = self.fat_graph.get_edge_data(fat1, fat2)
                        if data is None or data['weight'] > path.length:
                            self.fat_graph.insert_edge(
                                (
                                    fat1,
                                    fat2,
                                    {
                                        'weight': path.length,
                                        'linestring': path
                                    }
                                )
                            )

    def create_fat_graph(self) -> FATGraph:
        all_paths = list(self.all_paths_gdf.geometry)

        # insert edges
        for path in all_paths:
            path: LineString
            for i in range(self.fats_gdf.index.size):
                fat1 = self.fats_gdf.loc[i, self.fats_id_column]
                fat1_geom: Point = self.fats_gdf.loc[i, 'geometry']

                self._matches_line_end(
                    ends=(0, -1),
                    path=path,
                    fat1=fat1,
                    fat1_geom=fat1_geom,
                    i=i
                )
                # if Point(path.coords[0]).distance(fat1_geom) < self.tolerance:
                #     for j in range(self.fats_gdf.index.size): 
                #         if j != i:
                #             fat2 = self.fats_gdf.loc[j, self.fats_id_column]
                #             fat2_geom: Point = self.fats_gdf.loc[j, 'geometry']
                #             if Point(path.coords[-1]).distance(fat2_geom) < self.tolerance:
                #                 data = self.fat_graph.get_edge_data(fat1, fat2)
                #                 if data is None or data['weight'] > path.length:
                #                     self.fat_graph.insert_edge(
                #                         (
                #                             fat1,
                #                             fat2,
                #                             {
                #                                 'weight': path.length,
                #                                 'linestring': path
                #                             }
                #                         )
                #                     )

                self._matches_line_end(
                    ends=(-1, 0),
                    path=path,
                    fat1=fat1,
                    fat1_geom=fat1_geom,
                    i=i
                )
                # if Point(path.coords[-1]).distance(fat1_geom) < self.tolerance:
                #     for j in range(self.fats_gdf.index.size): 
                #         if j != i:
                #             fat2 = self.fats_gdf.loc[j, self.fats_id_column]
                #             fat2_geom: Point = self.fats_gdf.loc[j, 'geometry']
                #             if Point(path.coords[0]).distance(fat2_geom) < self.tolerance:
                #                 data = self.fat_graph.get_edge_data(fat1, fat2)
                #                 if data is None or data['weight'] > path.length:
                #                     self.fat_graph.insert_edge(
                #                         (
                #                             fat1,
                #                             fat2,
                #                             {
                #                                 'weight': path.length,
                #                                 'linestring': path
                #                             }
                #                         )
                #                     )

        return self.fat_graph
                    
