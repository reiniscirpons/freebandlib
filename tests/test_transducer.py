""" Tests for freebandlib.transducer """
from random import randint, random, shuffle
from typing import List

# import pytest  # type: ignore

from freebandlib.transducer import (
    InputLetter,
    StateId,
    Transducer,
    TransducerState,
)


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


def test_null():
    assert True
