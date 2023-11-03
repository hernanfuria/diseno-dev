from shapely.ops import Point, MultiPoint, LineString, MultiLineString
from shapely import unary_union


class Walker:
    """"""

    def __init__(
            self,
            previous: 'Walker' = None,
            next: list = None,  # list of Walkers
            current_pos: Point = None,
            target: Point = None,
            bloquers: list = None,  # list of Points
            path: MultiLineString = None,
            step_size: float = 1.0,
            reach_dist: float = 1.0
    ):
        # input checks
        # if not isinstance(previous, Walker):
        #     raise ValueError(f"previous: {previous} is not a Walker object")
        if not isinstance(current_pos, Point):
            raise ValueError(f"current_pos: {current_pos} is not a Point object")
        if not isinstance(target, Point):
            raise ValueError(f"target: {target} is not a Point object")
        if not (isinstance(path, MultiLineString) or isinstance(path, LineString)):
            raise ValueError(f"path: {path} is not a MultiLineString or LineString object")

        self.previous = previous
        self.next = next if next is not None else []
        self.current_pos = current_pos
        self.target = target
        self.bloquers = bloquers if bloquers is not None else []
        self.path = path
        self.step_size = step_size
        self.reach_dist = reach_dist

        self.is_path_end = False
        self.target_found = False

    def get_pos(self):
        return self.current_pos

    def _matches_previous(self, p: Point) -> bool:
        if self.previous is None:
            return False
        return p.distance(self.previous.get_pos()) < (self.reach_dist / 100)

    def _find_next_steps(self):
        # create a ring buffer of current_pos with radius step_size
        ring = self.current_pos.buffer(self.step_size).boundary

        # find intersections between path and ring
        inter = ring.intersection(self.path)

        # search the previous Walker inside intersections and delete it
        next_steps = []
        if isinstance(inter, Point):
            if not self._matches_previous(inter):
                next_steps = [inter]
        if isinstance(inter, MultiPoint):
            next_steps = []
            for p in list(inter.geoms):
                if not self._matches_previous(p):
                    next_steps.append(p)

        # return remaining intersections
        return [
            Walker(
                previous=self,
                current_pos=ns,
                target=self.target,
                bloquers=self.bloquers,
                path=self.path,
                step_size=self.step_size,
                reach_dist=self.reach_dist
            ) for ns in next_steps
        ]

    def _walk(self):
        # print(f"walking at {self}")
        # base case: if dist(current_pos, target) < reach_dist, end here (path found)
        if self.current_pos.distance(self.target) <= self.reach_dist:
            self.is_path_end = True
            self.target_found = True
            return [self.target_found, [self.current_pos]]

        # find next step(s)
        self.next = self._find_next_steps()

        # base case: if there are no next steps, end here (dead end)
        if self.next == []:
            self.is_path_end = False
            self.target_found = False
            return [self.target_found, [self.current_pos]]

        # call walk() for every next Walker
        for w in self.next:
            [tf, pos_list] = w._walk()
            if tf:
                return [True, [self.current_pos] + pos_list]

        return [False, []]

    def walk(self):
        [tf, pos_list] = self._walk()
        if tf:
            return pos_list

        return None

    def __str__(self):
        return f"Walker({self.current_pos.x}, {self.current_pos.y})"


def _tests():
    path = unary_union([
        LineString([(0, 0), (10, 0)]),
        LineString([(10, -1), (10, 11)]),
        LineString([(11, 10), (0, 10)]),
    ])
    # print(path, type(path))

    w = Walker(current_pos=Point(5, 0), target=Point(5, 10), path=path, step_size=0.1, reach_dist=0.05)
    # for ns in w._find_next_steps():
    #     print(ns)
    for p in w.walk():
        print(p)


    print("\033[32m _tests executed successfully \033[0m")


if __name__ == '__main__':
    print('\033[93m path_finder.py executed directly\n \033[0m')
    _tests()
