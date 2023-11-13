from src.logger import Logger
from src.clic import green


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
                    'length': 123
                    'linestring': <LineString object>
                }
            ), 
            (
                'f2',
                'f3',
                {
                    'length': 546
                    'linestring': <LineString object>
                }
            )
        ]
        """

        self.fats = fats
        self.adj_mat = [[None for _ in fats] for _ in fats]

        for edge in edges:
            self.insert_edge(edge)

        self.l = Logger(log_type='cli')

    def insert_edge(self, edge: tuple) -> None:
        """
        Inserts an edge in the FAT graph

        :param edge: Tuple containing 0: name of nap, 1: name of nap, 2: dict with data

        Example:
        edge <- (
                    'f1',
                    'f2',
                    {
                        'length': 123
                        'linestring': <LineString object>
                    }
                )
        """

        fat_1, fat_2, data = edge

        if not self.has_fat(fat_1):
            raise ValueError(f"Can't insert edge because {fat_1} is not in the graph")
        if not self.has_fat(fat_2):
            raise ValueError(f"Can't insert edge because {fat_2} is not in the graph")

        idx_1 = self._get_index_of_fat(fat_1)
        idx_2 = self._get_index_of_fat(fat_2)

        self.adj_mat[idx_1][idx_2] = data
        self.adj_mat[idx_2][idx_1] = data

    def has_fat(self, fat: str) -> bool:
        """
        :return: True if fat in FATGraph, False otherwise
        """

        return fat in self.fats

    def _get_index_of_fat(self, fat: str) -> int:
        """
        Returns index of FAT, returns -1 if not found

        :return: index (int) of parameter fat inside self.fats list
        """

        for f_idx, f in enumerate(self.fats):
            if f == fat:
                return f_idx
        return -1

    def _get_most_disconnected_fat(self, evaluate_data_key: str, ignore_fats: list = []) -> str:
        """
        Evaluates which FAT is the most disconnected from the rest 
        (ignoring specified FATs), and returns it
        """

        fat, fat_degree, total_weight = '', len(self.fats) + 1, 0

        for fat_row_idx, fat_row in enumerate(self.fats):
            if fat_row in ignore_fats:
                continue
            
            d = 0  # fat_row degree count
            tw = 0  # fat_row total weight sum

            for fat_col_idx, fat_col in enumerate(self.fats):
                if fat_col in ignore_fats:  # ignore this column
                    continue

                data = self.adj_mat[fat_row_idx][fat_col_idx]
                if data is None:  # there's no edge
                    continue

                d += 1
                tw += data[evaluate_data_key]

            if (d < fat_degree) or (d == fat_degree and tw > total_weight):
                fat, fat_degree, total_weight = fat_row, d, tw

        return fat

    def _create_group(self, n: int, evaluate_data_key: str, retrieve_data_key: str, ignore_fats: list = []) -> dict:
        """
        Constructs a group of n FATs using evaluate_data_key to minimize weights, 
        and retrieve_data_key to get the edge information.

        :return: Dict looking like this -> {
            'fats_in_group': ['f1', 'f2', 'f3', ...]
            'edges_in_group': [<edge_retrieved_data>, <edge_retrieved_data>, ...]
        }
        """

        fats_in_group = [self._get_most_disconnected_fat(evaluate_data_key, ignore_fats)]
        edges = []
        
        while len(fats_in_group) < n:
            self._log(f"Group in progress {fats_in_group}")
            edge_row, edge_col, weight = 0, 0, 0
            for fat_row in fats_in_group:
                fat_row_idx = self._get_index_of_fat(fat_row)


                for fat_col_idx, fat_col in enumerate(self.fats):

                    if fat_col in ignore_fats + fats_in_group:  # ignore this column
                        continue

                    data = self.adj_mat[fat_row_idx][fat_col_idx]
                    if data is None:  # there's no edge
                        continue

                    if weight == 0 or data[evaluate_data_key] < weight:
                        edge_row, edge_col, weight = fat_row_idx, fat_col_idx, data[evaluate_data_key]

            if weight != 0:
                fats_in_group.append(self.fats[edge_col])
                edges.append((edge_row, edge_col))
                self._log(f"{self.fats[edge_col]}, edge {(edge_row, edge_col)} added to group")
            else:  # can't find more fats
                break

        edges_in_group = []
        for edge_row, edge_col in edges:
            data = self.adj_mat[edge_row][edge_col]
            edges_in_group.append(data[retrieve_data_key])

        return {
            'fats_in_group': fats_in_group,
            'edges_in_group': edges_in_group
        }

    def group_by_n(self, n: int, evaluate_data_key: str, retrieve_data_key: str) -> list:
        """
        Constructs groups of n FATs (max) using evaluate_data_key to minimize weights, 
        and retrieve_data_key to get the edge information.

        :return: List of dicts looking like this -> [
            {
                'fats_in_group': ['f1', 'f2', 'f3', ...]
                'edges_in_group': [<edge_retrieved_data>, <edge_retrieved_data>, ...]
            },
            {
                'fats_in_group': ['f4', 'f5', 'f6', ...]
                'edges_in_group': [<edge_retrieved_data>, <edge_retrieved_data>, ...]
            },
            ...
        ]
        """

        ignore_fats = []
        groups = []

        all_grouped = False
        while not all_grouped:
            group = self._create_group(n, evaluate_data_key, retrieve_data_key, ignore_fats)
            groups.append(group)
            self._log(green('New group created'))
            self._log(green(f"\tFATs:  {group['fats_in_group']}"))
            self._log(green(f"\tedges: {group['edges_in_group']}"))

            ignore_fats += group['fats_in_group']
            all_grouped = True
            for fat in self.fats:
                if fat not in ignore_fats:
                    all_grouped = False
                    break

        return groups

    def _log(self, log: str) -> None:
        """Handles the log"""
        
        self.l.log(log)

    def __str__(self) -> str:
        text = 'FATGraph\nFATs\n'
        text += f'\t{self.fats}\n'
        text += f'edges\n'
        for f1_idx, f1 in enumerate(self.fats):
            for f2_idx, f2 in enumerate(self.fats):
                data = self.adj_mat[f1_idx][f2_idx]
                if f1_idx <= f2_idx and data is not None:
                    text += f'\t< {f1} >---{data}---< {f2} >\n'

        return text