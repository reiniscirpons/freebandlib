""" Tests for freebandlib.transducer """
import itertools
from random import randint, random, shuffle
from typing import List, Optional

import pytest
from freebandlib.transducer import (
    StateId,
    Transducer,
    interval_transducer,
    minimal_transducer,
    transducer_connected_states,
    transducer_isomorphism,
    transducer_minimize,
    transducer_topological_order,
    transducer_trim,
    treelike_transducer,
    transducer_induced_subtransducer,
)
from freebandlib.words import (
    InputLetter,
    OutputLetter,
    OutputWord,
    cont,
    word_function,
)

########################################################################
# Checker functions
########################################################################


def check_transducer_realize(w: OutputWord, t: Transducer) -> None:
    N = len(cont(w))
    fw = word_function(w)
    for i in range(N + 2):
        for x in itertools.product(*[[0, 1]] * i):
            assert t.traverse(x) == fw(x)


def check_transducers_realize_same(
    w: OutputWord, t1: Transducer, t2: Transducer
) -> None:
    N = len(cont(w))
    for i in range(N + 2):
        for x in itertools.product(*[[0, 1]] * i):
            assert t1.traverse(x) == t2.traverse(x)


def check_transducer_topo_order(t: Transducer) -> None:
    top = transducer_topological_order(t)
    assert top is None or isinstance(top, list)
    if top is None:
        return
    assert len(top) == t.nr_states
    nbs = t.underlying_digraph()
    for v, nbs_v in enumerate(nbs):
        for w in nbs_v:
            assert top.index(w) > top.index(v)


def check_transducer_trim(w: OutputWord, t: Transducer) -> None:
    trimmed_t = transducer_trim(t)
    check_transducers_realize_same(w, t, trimmed_t)
    assert len(transducer_connected_states(trimmed_t)) == trimmed_t.nr_states
    if t.nr_states == trimmed_t.nr_states:
        assert transducer_isomorphism(t, trimmed_t)

    double_trimmed_t = transducer_trim(trimmed_t)
    assert transducer_isomorphism(double_trimmed_t, trimmed_t)


########################################################################
# Helper functions
########################################################################


def random_transducer(
    nr_states: int,
    output_alphabet: int,
    edge_prob: float,
    terminal_prob: float,
    initial_prob: float,
    acyclic: bool = False,
) -> Transducer:
    """Generate a random transducer.

    Parameters
    ----------
    nr_states: int
        The number of states in the final transducer
    output_alphabet: int
        The size of the output alpbhabet
    edge_prob: float
        The probability of a transition existing.
    terminal_prob: float
        The probability of a state being terminal.
    initial_prob: float
        The probability of there existing an initial state
    acyclic: bool, default=False
        If set to True then forces the transducer to be acyclic.

    Returns
    -------
    Transducer
        A randomly generated transducer with the specified parameters.
    """

    transducer = Transducer(None, [], [], [])

    if nr_states <= 0:
        return transducer

    states = list(range(nr_states))
    shuffle(states)

    for state in states:
        next_state: List[Optional[StateId]] = [None, None]
        next_letter: List[Optional[OutputLetter]] = [None, None]
        terminal = False
        for letter in [0, 1]:
            if random() < edge_prob:
                if acyclic and state != nr_states - 1:
                    next_letter[letter] = randint(0, output_alphabet - 1)
                    next_state[letter] = states[
                        randint(state + 1, nr_states - 1)
                    ]
                elif not acyclic:
                    next_letter[letter] = randint(0, output_alphabet - 1)
                    next_state[letter] = states[randint(0, nr_states - 1)]
        if random() < terminal_prob:
            terminal = True
        # This might add an invalid state stha
        transducer.add_state(next_state, next_letter, terminal)

    if random() < initial_prob:
        transducer.initial = states[0]
    return transducer


########################################################################
# Test cases
########################################################################


def test_transducer_validate():
    try:
        t = Transducer(None, [], [], [])
    except RuntimeError as e:
        assert False, f'empty transducer raised the exception "{e}"'
    assert transducer_connected_states(t) == []
    assert t.underlying_digraph() == []
    assert t.traverse([]) is None

    with pytest.raises(RuntimeError):
        t = Transducer(0, [None], [None], [False])

    with pytest.raises(RuntimeError):
        t = Transducer(True, [None], [None], [False])
    with pytest.raises(RuntimeError):
        t = Transducer("a", [None], [None], [False])

    with pytest.raises(RuntimeError):
        t = Transducer(None, [], [], None)

    with pytest.raises(RuntimeError):
        t = Transducer(None, [], [], [None])

    with pytest.raises(RuntimeError):
        t = Transducer(None, [], [], [True])

    with pytest.raises(RuntimeError):
        t = Transducer(None, [], [], [], ["a"])


def test_transducer_repr():
    t = treelike_transducer([0, 1, 0, 2])
    assert (
        t.__repr__()
        == "(0, [[1, 8], [2, 5], [3, 4], [None, None], [None, None], [6, 7], [None, None], [None, None], [9, 12], [10, 11], [None, None], [None, None], [13, 14], [None, None], [None, None]], [[2, 1], [1, 1], [0, 0], [None, None], [None, None], [0, 0], [None, None], [None, None], [2, 0], [0, 0], [None, None], [None, None], [2, 2], [None, None], [None, None]], [False, False, False, True, True, False, True, True, False, False, True, True, False, True, True])"
    )


def test_treelike_transducer_abac():
    t = treelike_transducer([0, 1, 0, 2])

    assert t.nr_states == 15
    assert t.next_state[0] == [1, 8]
    assert t.traverse([0, 0]) is None
    assert t.traverse([0, 0, 0, 0]) is None
    assert t.traverse([0, 0, 0]) == [2, 1, 0]
    assert t.traverse([0, 0, 1]) == [2, 1, 0]
    assert t.traverse([0, 1, 0]) == [2, 1, 0]
    assert t.traverse([0, 1, 1]) == [2, 1, 0]
    assert t.traverse([1, 0, 0]) == [1, 2, 0]
    assert t.traverse([1, 0, 1]) == [1, 2, 0]
    assert t.traverse([1, 1, 0]) == [1, 0, 2]
    assert t.traverse([1, 1, 1]) == [1, 0, 2]
    assert t.underlying_digraph() == [
        [1, 8],
        [2, 5],
        [3, 4],
        [],
        [],
        [6, 7],
        [],
        [],
        [9, 12],
        [10, 11],
        [],
        [],
        [13, 14],
        [],
        [],
    ]
    assert transducer_connected_states(t) == [
        0,
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9,
        10,
        11,
        12,
        13,
        14,
    ]


def test_interval_transducer_abac():
    w = [0, 1, 0, 2]
    t = interval_transducer(w)
    assert t.nr_states == 11
    assert transducer_connected_states(t) == [0, 1, 3, 4, 5, 7, 9]
    assert t.traverse([0, 0, 0]) == [2, 1, 0]


def test_minimal_transducer_abac():
    w = [0, 1, 0, 2]
    t = minimal_transducer(w)
    assert t.nr_states == 6
    assert transducer_connected_states(t) == [0, 1, 2, 3, 4, 5]
    assert t.traverse([0, 0, 0]) == [2, 1, 0]


def test_treelike_transducer_abac_realize():
    w = [0, 1, 0, 2]
    t = treelike_transducer(w)
    check_transducer_realize(w, t)


def test_interval_transducer_abac_realize():
    w = [0, 1, 0, 2]
    t = interval_transducer(w)
    check_transducer_realize(w, t)


def test_minimal_transducer_abac_realize():
    w = [0, 1, 0, 2]
    t = minimal_transducer(w)
    check_transducer_realize(w, t)


def test_all_transducers_equiv_abac():
    w = [0, 1, 0, 2]
    check_transducers_realize_same(
        w, treelike_transducer(w), interval_transducer(w)
    )
    check_transducers_realize_same(
        w, treelike_transducer(w), minimal_transducer(w)
    )
    check_transducers_realize_same(
        w, interval_transducer(w), minimal_transducer(w)
    )


def test_transducer_topo_order():
    t = treelike_transducer([0, 1, 0, 2])
    assert transducer_topological_order(t) == [
        0,
        1,
        8,
        2,
        5,
        9,
        12,
        3,
        4,
        6,
        7,
        10,
        11,
        13,
        14,
    ]
    check_transducer_topo_order(t)
    check_transducer_topo_order(interval_transducer([0, 1, 0, 2]))
    check_transducer_topo_order(minimal_transducer([0, 1, 0, 2]))


def test_transducer_trim():

    w = [0, 1, 0, 2]
    check_transducer_trim(w, treelike_transducer(w))
    check_transducer_trim(w, interval_transducer(w))
    check_transducer_trim(w, minimal_transducer(w))

    w = [0, 1, 2, 3, 0, 3, 1, 3, 2, 1, 0, 0]
    check_transducer_trim(w, treelike_transducer(w))
    check_transducer_trim(w, interval_transducer(w))
    check_transducer_trim(w, minimal_transducer(w))

    t = Transducer(None, [], [], [])
    assert transducer_isomorphism(t, transducer_trim(t))


def test_transducer_isomorphism():
    t = Transducer(None, [], [], [])
    assert transducer_isomorphism(t, t)

    w = [0, 1, 0, 2]
    t = interval_transducer(w)

    with pytest.raises(RuntimeError):
        transducer_isomorphism(t, t)
    with pytest.raises(RuntimeError):
        transducer_isomorphism(treelike_transducer(w), t)
    assert not transducer_isomorphism(
        treelike_transducer(w), transducer_trim(t)
    )

    u = [0, 1, 2, 3]
    assert not transducer_isomorphism(
        treelike_transducer(w), treelike_transducer(u)
    )

    v = [1, 0, 2, 1]
    assert not transducer_isomorphism(
        treelike_transducer(w), treelike_transducer(v)
    )

    t1 = treelike_transducer(v)
    assert t1.nr_states == 15
    assert transducer_connected_states(t1) == [
        0,
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9,
        10,
        11,
        12,
        13,
        14,
    ]
    t2 = transducer_induced_subtransducer(t1, list(range(8)))
    t3 = transducer_induced_subtransducer(t1, [0] + list(range(8, 15)))
    assert t1.nr_states == len(transducer_connected_states(t1))
    assert t2.nr_states == t3.nr_states
    assert not transducer_isomorphism(t2, t3)


def test_transducer_minimize():
    t = Transducer(None, [], [], [])
    assert transducer_isomorphism(t, transducer_minimize(t))
