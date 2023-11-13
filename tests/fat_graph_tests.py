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


def _tests():
    _test1()


if __name__ == "__main__":
    print(orange("fat_graph_tests.py executed directly\n"))
    _tests()