class FATGraph:
    """"""

    def __init__(self, fats: list, edges: list = None) -> None:
        """
        :param fats: List of FATs names (str)
        :param edges: List of 3-tuples, each one containing 0: name of nap, 1: name of nap, 2: dict with data

        Example:
        fats <- ['f1', 'f2', 'f3']
        edges <- [
            (
                'f1',
                'f2',
                {
                    'weight': 123
                    'linestring': <LineString object>
                }
            ), 
            (
                'f2',
                'f3',
                {
                    'weight': 546
                    'linestring': <LineString object>
                }
            )
        ]
        """

        self.fats = fats
        self.adj_mat = [[None for _ in fats] for _ in fats]

    def insert_edge(self, edge: tuple) -> None:
        """
        Inserts an edge in the FAT graph

        :param edge: Tuple containing 0: name of nap, 1: name of nap, 2: dict with data

        Example:
        edge <- (
                    'f1',
                    'f2',
                    {
                        'weight': 123
                        'linestring': <LineString object>
                    }
                )
        """
        # fat_1, fat_2, data = edge

    def _get_index_of_fat(self, fat: str) -> int:
        """
        Returns index of FAT

        :return: index (int) of parameter fat inside self.fats list
        """
        return 0

    def _get_most_disconnected_fat(self):
        pass

    def _create_group(self):
        pass

    def group_by_n(self):
        pass

    def _log(self):
        """Handles the log"""
        pass