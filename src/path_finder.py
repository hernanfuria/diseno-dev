from shapely.ops import Point, LineString, MultiLineString


class Walker:
    """"""

    def __init__(
            self,
            previous: 'Walker' = None,
            next: list = None,  # list of Points
            sPoint: Point = None,
            target: Point = None,
            bloquers: list = None  # list of Points
    ):
        if isinstance(previous, Walker):
            raise ValueError(f"previous: {previous} is not a Walker object")
        if isinstance(sPoint, Point):
            raise ValueError(f"sPoint: {sPoint} is not a Point object")
        if isinstance(target, Point):
            raise ValueError(f"target: {target} is not a Point object")

        self.previous = previous
        self.next = next if next is not None else []
        self.sPoint = sPoint
        self.target = target
        self.bloquers = bloquers if bloquers is not None else []

        self.is_path_end = False
        self.target_found = False

    def _find_next_step(self):
        pass

    def walk(self):
        pass