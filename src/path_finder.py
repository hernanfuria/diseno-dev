from shapely.ops import Point, MultiPoint, LineString, MultiLineString


class Walker:
    """"""

    def __init__(
            self,
            previous: 'Walker' = None,
            next: list = None,  # list of Walkers
            current_pos: Point = None,
            target: Point = None,
            bloquers: list = None,  # list of Points
            path: MultiLineString | LineString = None,
            step_size: float = 1.0,
            reach_dist: float = 1.0
    ):
        # input checks
        if not isinstance(previous, Walker):
            raise ValueError(f"previous: {previous} is not a Walker object")
        if not isinstance(current_pos, Point):
            raise ValueError(f"current_pos: {current_pos} is not a Point object")
        if not isinstance(target, Point):
            raise ValueError(f"target: {target} is not a Point object")
        if not isinstance(path, MultiLineString) or not isinstance(path, LineString):
            raise ValueError(f"path: {path} is not a Point object")

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
        return p.distance(self.previous.get_pos()) < (self.reach_dist / 100)

    def _find_next_steps(self):
        # create a ring buffer of current_pos with radius step_size
        ring = self.current_pos.buffer(self.step_size).boundary

        # find intersections between path and ring
        inter = ring.intersection(self.path)

        # search the previous Walker inside intersections and delete it
        if isinstance(inter, Point):
            if self._matches_previous(inter):
                return []
        if isinstance(inter, MultiPoint):
            next_steps = []
            for p in list(inter.geoms):
                if not self._matches_previous(p):
                    next_steps.append(p)

            return next_steps

        # return remaining intersections
        pass

    def walk(self):
        # base case: if dist(current_pos, target) < reach_dist, end here (path found)

        # find next step(s)
        # base case: if there are no next steps, end here (dead end)

        # call walk() for every next Walker
        pass