"""Graph utility functions."""
from typing import List, Optional

DigraphVertex = int
DigraphAdjacencyList = List[List[DigraphVertex]]


def digraph_reverse(digraph: DigraphAdjacencyList) -> DigraphAdjacencyList:
    """Create the reverse digraph of the input.

    Does not modify the input digraph.

    Parameters
    ----------
    digraph: DigraphAdjacencyList
        An adjacency list.

    Returns
    -------
    DigraphAdjacencyList
        An adjacency list of the reverse digraph.

    Notes
    -----
    The reverse digraph of a digraph has the same vertices but has each edge
    is reversed, i.e. the reverse digraph has a directed edge :math:`(u, v)`
    if and only there is an edge :math:`(v, u)` in the original graph.
    """
    result: DigraphAdjacencyList = [[] for _ in digraph]

    vertex_u: DigraphVertex
    vertex_v: DigraphVertex
    neighbours_u: List[DigraphVertex]
    for vertex_u, neighbours_u in enumerate(digraph):
        for vertex_v in neighbours_u:
            result[vertex_v].append(vertex_u)

    return result


def digraph_is_reachable(
    digraph: DigraphAdjacencyList, start: List[DigraphVertex]
) -> List[bool]:
    """For each vertex determine if it can be reached from any start vertex.

    Parameters
    ----------
    digraph: DigraphAdjacencyList
        An adjacency list.
    start: List[DigraphVertex]
        The list of starting vertices.

    Returns
    -------
    is_reachable: List[bool]
        A list such that `is_reachable[v]` is `True` whenever `v` is reachable
        from some starting vertex and `False` otherwise.

    Notes
    -----
    A vertex `v` is reachable from a vertex `u` if there is a directed path
    starting at `u` and ending in `v`.

    This is calculated by using a breadth first traversal.
    """
    i: int = 0
    is_reachable: List[bool] = [False for _ in digraph]
    vertex_u: DigraphVertex
    for vertex_u in start:
        is_reachable[vertex_u] = True

    vertex_v: DigraphVertex
    que: List[DigraphVertex] = start[::]
    while i < len(que):
        vertex_u = que[i]
        for vertex_v in digraph[vertex_u]:
            if not is_reachable[vertex_v]:
                que.append(vertex_v)
                is_reachable[vertex_v] = True
        i += 1

    return is_reachable


def digraph_topological_order(
    digraph: DigraphAdjacencyList,
) -> Optional[List[DigraphVertex]]:
    """Return the digraph vertices in topological order if possible.

    Returns `None` if the digraph contains a directed cycle.

    Parameters
    ----------
    digraph: DigraphAdjacencyList
        An adjacency list.

    Returns
    -------
    Optional[List[DigraphVertex]]
        A list of vertices in topological order, if such an order exists, and
        `None` otherwise.

    Notes
    -----
    We say that the vertices are in topological order if no child vertex occurs
    before its parent in the ordering. Such an ordering exists if and only if
    the digraph contains no ordered cycle.

    This is calculated using Kahn's algorithm.
    """
    times_seen: List[int] = [0 for _ in digraph]
    vertex_u: DigraphVertex
    vertex_v: DigraphVertex
    neighbours_u: List[DigraphVertex]
    for vertex_u, neighbours_u in enumerate(digraph):
        for vertex_v in neighbours_u:
            times_seen[vertex_v] += 1

    topo_order: List[DigraphVertex] = [
        u for u, t in enumerate(times_seen) if t == 0
    ]
    i: int = 0
    while i < len(topo_order):
        vertex_u = topo_order[i]
        for vertex_v in digraph[vertex_u]:
            times_seen[vertex_v] -= 1
            if times_seen[vertex_v] == 0:
                topo_order.append(vertex_v)
        i += 1

    if len(topo_order) != len(digraph):
        return None

    return topo_order
