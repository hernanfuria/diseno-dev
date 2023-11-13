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

def _tests():
    _test2()


if __name__ == "__main__":
    print(orange("fat_graph_tests.py executed directly\n"))
    _tests()