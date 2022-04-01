""" Tests for freebandlib.transducer """
from random import randint, random, shuffle
from typing import List

import pytest
from freebandlib.transducer import (
    Transducer,
    TransducerState,
    transducer_connected_states,
    treelike_transducer,
    transducer_topological_order,
)
from freebandlib.words import InputLetter, StateId, pref_ltof, suff_ftol


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

    if nr_states <= 0:
        return Transducer(None, [], [])

    state_ids: List[StateId] = list(range(-10 * nr_states, 10 * nr_states))
    shuffle(state_ids)
    state_ids = state_ids[:nr_states]

    state_id: StateId
    states: List[TransducerState] = [
        TransducerState(state_id, [None, None], [None, None])
        for state_id in state_ids
    ]

    state: TransducerState
    letter: InputLetter
    initial_id: StateId = states[0]
    for state_id, state in enumerate(states):
        for letter in [0, 1]:
            if random() < edge_prob:
                if acyclic and state_id != nr_states - 1:
                    state.next_letter[letter] = randint(0, output_alphabet - 1)
                    state.next_state[letter] = states[
                        randint(state_id + 1, nr_states - 1)
                    ]
                elif not acyclic:
                    state.next_letter[letter] = randint(0, output_alphabet - 1)
                    state.next_state[letter] = states[randint(0, nr_states - 1)]
    shuffle(states)
    for state_id, state in enumerate(states):
        if state.state_id == initial_id:
            initial_id = state_id
            break

    terminal: List[bool] = []
    for state in states:
        if random() < terminal_prob:
            terminal.append(True)
        else:
            terminal.append(False)

    if random() < initial_prob:
        return Transducer(initial_id, states, terminal)
    return Transducer(None, states, terminal)


def test_transducer_validate():
    try:
        t = Transducer(None, [], [])
    except RuntimeError as e:
        assert False, f'empty transducer raised the exception "{e}"'
    assert transducer_connected_states(t) == []
    assert t.underlying_digraph() == []
    assert t.traverse([]) is None

    with pytest.raises(RuntimeError):
        t = Transducer(0, [None], [False])


def test_transducer_abac():
    t = treelike_transducer([0, 1, 0, 2])

    assert len(t.states) == 15
    assert isinstance(t.states[0], TransducerState)
    assert t.states[0].__repr__() == "(0, [1, 8], [2, 1])"
    assert t.states[0].next_state_id() == [1, 8]
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


def check_transducer_topo_order(t):
    top = transducer_topological_order(t)
    assert top is None or isinstance(top, list)
    if top is None:
        return
    assert len(top) == len(t.states)
    nbs = t.underlying_digraph()
    for v, nbs_v in enumerate(nbs):
        for w in nbs_v:
            assert top.index(w) > top.index(v)


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
