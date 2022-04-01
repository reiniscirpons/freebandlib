""" Tests for freebandlib.digraph """
from typing import List, Optional

import pytest  # type: ignore

from freebandlib.digraph import (
    DigraphAdjacencyList,
    DigraphVertex,
    digraph_is_reachable,
    digraph_reverse,
    digraph_topological_order,
)


@pytest.mark.parametrize(
    "digraph, reverse_digraph",
    [
        ([], []),
        ([[]], [[]]),
        ([[], []], [[], []]),
        ([[0]], [[0]]),
        ([[1], []], [[], [0]]),
        ([[1], [1]], [[], [0, 1]]),
        ([[1], [0, 1]], [[1], [0, 1]]),
        ([[1], [2], [0]], [[2], [0], [1]]),
        ([[1], [2], [0], []], [[2], [0], [1], []]),
        (
            [[0, 1, 1, 3], [0, 0, 3, 0], [0], [2, 2]],
            [[0, 1, 1, 1, 2], [0, 0], [3, 3], [0, 1]],
        ),
    ],
)
def test_digraph_reverse(
    digraph: DigraphAdjacencyList, reverse_digraph: DigraphAdjacencyList
):
    """Check that digraph_reverse is working correctly."""
    digraph_copy = [neighbours[::] for neighbours in digraph]
    result: DigraphAdjacencyList = digraph_reverse(digraph)

    # Check that there are no side-effects
    assert digraph == digraph_copy

    # Vertex indices should be preserved, but the ordering of the neighbours
    # does not have to be
    for neighbours in result:
        neighbours.sort()

    assert result == reverse_digraph

    # Check self inverse
    result = digraph_reverse(result)
    for neighbours in result:
        neighbours.sort()
    for neighbours in digraph:
        neighbours.sort()
    assert result == digraph

    result = digraph_reverse(reverse_digraph)
    for neighbours in result:
        neighbours.sort()
    assert result == digraph


@pytest.mark.parametrize(
    "digraph, start, is_reachable",
    [
        ([], [], []),
        ([[]], [], [False]),
        ([[]], [0], [True]),
        ([[], []], [], [False, False]),
        ([[], []], [0], [True, False]),
        ([[], []], [1], [False, True]),
        ([[], []], [1, 0], [True, True]),
        ([[0]], [0], [True]),
        ([[0]], [], [False]),
        ([[1], []], [], [False, False]),
        ([[1], []], [0], [True, True]),
        ([[1], []], [1], [False, True]),
        ([[1], []], [0, 1], [True, True]),
        ([[1], [1]], [], [False, False]),
        ([[1], [1]], [0], [True, True]),
        ([[1], [1]], [1], [False, True]),
        ([[1], [1]], [0, 1], [True, True]),
        ([[1], [0, 1]], [], [False, False]),
        ([[1], [0, 1]], [0], [True, True]),
        ([[1], [0, 1]], [1], [True, True]),
        ([[1], [0, 1]], [0, 1], [True, True]),
        ([[1], [2], [0]], [], [False, False, False]),
        ([[1], [2], [0]], [0], [True, True, True]),
        ([[1], [2], [0]], [1], [True, True, True]),
        ([[1], [2], [0]], [2], [True, True, True]),
        ([[1], [2], [0]], [0, 1], [True, True, True]),
        ([[1], [2], [0]], [0, 2], [True, True, True]),
        ([[1], [2], [0]], [1, 2], [True, True, True]),
        ([[1], [2], [0]], [0, 1, 2], [True, True, True]),
        (
            [[0, 1, 1, 3], [0, 0, 3, 0], [0], [2, 2]],
            [],
            [False, False, False, False],
        ),
        (
            [[0, 1, 1, 3], [0, 0, 3, 0], [0], [2, 2]],
            [0],
            [True, True, True, True],
        ),
        (
            [[0, 1, 1, 3], [0, 0, 3, 0], [0], [2, 2]],
            [2, 1],
            [True, True, True, True],
        ),
        (
            [[0, 1], [0, 2, 2], [3, 3], [2, 2, 3, 3]],
            [],
            [False, False, False, False],
        ),
        (
            [[0, 1], [0, 2, 2], [3, 3], [2, 2, 3, 3]],
            [0],
            [True, True, True, True],
        ),
        (
            [[0, 1], [0, 2, 2], [3, 3], [2, 2, 3, 3]],
            [1],
            [True, True, True, True],
        ),
        (
            [[0, 1], [0, 2, 2], [3, 3], [2, 2, 3, 3]],
            [0, 1],
            [True, True, True, True],
        ),
        (
            [[0, 1], [0, 2, 2], [3, 3], [2, 2, 3, 3]],
            [0, 2],
            [True, True, True, True],
        ),
        (
            [[0, 1], [0, 2, 2], [3, 3], [2, 2, 3, 3]],
            [2, 2],
            [False, False, True, True],
        ),
        (
            [[0, 1], [0, 2, 2], [3, 3], [2, 2, 3, 3]],
            [2, 3],
            [False, False, True, True],
        ),
        (
            [[0, 1], [0, 2, 2], [3, 3], [2, 2, 3, 3]],
            [3],
            [False, False, True, True],
        ),
        (
            [[0, 1], [0, 2, 2, 5], [3, 3], [2, 2, 3], [1], []],
            [0],
            [True, True, True, True, False, True],
        ),
        (
            [[0, 1], [0, 2, 2, 5], [3, 3], [2, 2, 3], [1], []],
            [1],
            [True, True, True, True, False, True],
        ),
        (
            [[0, 1], [0, 2, 2, 5], [3, 3], [2, 2, 3], [1], []],
            [2],
            [False, False, True, True, False, False],
        ),
        (
            [[0, 1], [0, 2, 2, 5], [3, 3], [2, 2, 3], [1], []],
            [3],
            [False, False, True, True, False, False],
        ),
        (
            [[0, 1], [0, 2, 2, 5], [3, 3], [2, 2, 3], [1], []],
            [4],
            [True, True, True, True, True, True],
        ),
        (
            [[0, 1], [0, 2, 2, 5], [3, 3], [2, 2, 3], [1], []],
            [5],
            [False, False, False, False, False, True],
        ),
        (
            [[0, 1], [0, 2, 2, 5], [3, 3], [2, 2, 3], [1], []],
            [2, 5],
            [False, False, True, True, False, True],
        ),
    ],
)
def test_digraph_is_reachable(
    digraph: DigraphAdjacencyList,
    start: List[DigraphVertex],
    is_reachable: List[bool],
):
    """Check that digraph_is_reachable is working correctly."""
    assert digraph_is_reachable(digraph, start) == is_reachable


@pytest.mark.parametrize(
    "digraph, orders",
    [
        ([], [[]]),
        ([[]], [[0]]),
        ([[0]], [None]),
        ([[1], []], [[0, 1]]),
        ([[], [0]], [[1, 0]]),
        ([[1], [0]], [None]),
        ([[], []], [[0, 1], [1, 0]]),
        ([[1, 2], [], []], [[0, 1, 2], [0, 2, 1]]),
        ([[1, 2], [2], []], [[0, 1, 2]]),
        ([[1], [2], []], [[0, 1, 2]]),
        ([[1], [], [1]], [[0, 2, 1], [2, 0, 1]]),
        ([[1, 1, 1], [], [1]], [[0, 2, 1], [2, 0, 1]]),
        ([[1, 1, 1], [], [0]], [[2, 0, 1]]),
        ([[1, 1, 1], [2, 2], [0]], [None]),
        ([[1, 1, 1, 2, 2, 2], [3, 3], [], [2, 2]], [[0, 1, 3, 2]]),
    ],
)
def test_digraph_topological_sort(
    digraph: DigraphAdjacencyList, orders: List[Optional[List[DigraphVertex]]]
):
    """Check that digraph_topological_sort is working correctly."""
    assert digraph_topological_order(digraph) in orders
