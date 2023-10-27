from __future__ import annotations


class _Node:
    """Node inside the graph. Holds a value."""

    def __init__(self, value) -> None:
        self.value = value

    def setValue(self, value):
        """Sets the value stored in the Node."""

        self.value = value

    def getValue(self):
        """Returns the value stored in the Node."""

        return self.value

    def __str__(self):
        return self.value

    def __eq__(self, other: _Node):
        return self.value == other.value


class _Edge:
    """Representation of a weighted Edge that connects two Nodes."""

    def __init__(self, endpoint0: _Node, endpoint1: _Node, weight: int | float = 1 ) -> None:
        self.endpoints = [endpoint0, endpoint1]
        self.weight = weight

    def setEndpoint(self, node: _Node, position: int) -> None:
        """
        Sets one endpoint of the Edge. `position` (0 or 1) defines the end of the Edge to
        which the `node` is connected.
        """

        if position < 0 or position > 1:
            raise Exception(f"Invalid position {position}, it must be 0 or 1.")

        self.endpoints[position] = node

    def getEndpoint(self, position: int) -> _Node:
        """Returns the Node connected to the edge at the specified `position` (0 or 1)."""

        if position < 0 or position > 1:
            raise Exception(f"Invalid position {position}, it must be 0 or 1.")

        return self.endpoints[position]

    def __str__(self):
        return f"{self.endpoints[0].getValue()}---< w = {self.weight} >---{self.endpoints[1].getValue()}"

    def __eq__(self, other: _Edge):
        comp = [
            self.endpoints == other.endpoints,
            self.weight == other.weight
        ]

        return False not in comp


class Graph:
    """"""

    def __init__(self):
        self.nodes = []
        self.edges = []

    def addNode(self, value):
        """Adds a Node with a `value` to the Graph"""

        self.nodes.append(_Node(value=value))

    def getNode(self, value):
        """Returns the first appearance of a Node which value matches the `value` parameter."""

        for n in self.nodes:
            if n.getValue() == value:
                return n

        return None

    def hasNode(self, value) -> bool:
        """Returns True if the Graph contains a Node with value `value`, returns False otherwise."""

        for n in self.nodes:
            if n.getValue() == value:
                return True

        return False

    def removeNode(self, value) -> bool:
        """
        Removes the first appearance of a Node which value matches the `value` parameter.
        Returns True if a Node was removed, returns False otherwise.
        """

    def addEdge(self, value0, value1, weight: int | float = 1):
        """Adds an Edge that connects `value0` and `value1` (if the Nodes exist) with `weight` to the Graph."""

    def hasEdge(self, value0, value1, weight: int | float = 1) -> bool:
        """Returns True if the Graph contains an Edge with values `value0` and `value1`, and weight `weight`,
        returns False otherwise."""

    def getEdge(self, value0, value1) -> _Edge | None:
        """Returns the first appearance of an Edge which values matches the `value0` and `value1` parameters."""

    def removeEdge(self, value0, value1) -> bool:
        """
        Removes the first appearance of an Edge which values matches the `value0` and `value1` parameters.
        Returns True if an Edge was removed, returns False otherwise.
        """

    def __str__(self):
        pass


def _tests():
    n = _Node(1)
    print(n)
    assert n.getValue() == 1

    print("\033[32m _tests executed successfully \033[0m")


if __name__ == '__main__':
    print('\033[93m graph.py executed directly\n \033[0m')
    _tests()
