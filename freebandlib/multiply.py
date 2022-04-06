"""Transducer multiplication functions.

TODO: Finish
"""

from typing import List, Optional

from freebandlib.words import OutputLetter
from freebandlib.transducer import (
    StateId,
    Transducer,
    transducer_precompute_q,
    transducer_cont,
)


def compute_k(
    alpha: int, transducer_x: Transducer, transducer_y: Transducer
) -> List[List[Optional[int]]]:
    r"""Given a transducer return the K function.

    Parameters
    ----------
    alpha: int
        Should be 0 or 1
    transducer_x : Transducer
        A transducer representing :math:`x\in\FB(A)`.
    transducer_y : Transducer
        A transducer representing :math:`y\in\FB(A)`.

    Returns
    -------
    List[List[int]]
        The partial function :math:`\overline{K}_{\alpha}` implemented as a
        two dimensional list.
    """
    q_x = transducer_precompute_q(transducer_x, 1)
    q_y = transducer_precompute_q(transducer_y, 0)
    cont_x = transducer_cont(transducer_x)
    cont_y = transducer_cont(transducer_y)
    K: List[List[Optional[int]]] = [
        [None for j in range(len(cont_y) + 1)] for i in range(len(cont_x) + 1)
    ]
    c = set()
    if alpha == 0:
        for i in range(len(cont_x), -1, -1):
            for j in range(len(cont_y), -1, -1):
                state = transducer_y.states[q_y[j]]
                letter = state.next_letter[0]
                if letter is not None and letter not in c:
                    K[i][j] = 1
                elif (
                    letter is not None
                    and j + 1 <= len(cont_y)
                    and K[i][j + 1] is not None
                ):
                    K[i][j] = 1 + K[i][j + 1]
            if i != 0:
                state = transducer_x.states[q_x[i - 1]]
                letter = state.next_letter[1]
                c.add(letter)
        return K
    # TODO: Remove code duplication
    # alpha == 1
    for j in range(len(cont_y), -1, -1):
        for i in range(len(cont_x), -1, -1):
            state = transducer_x.states[q_x[i]]
            letter = state.next_letter[1]
            if letter is not None and letter not in c:
                K[i][j] = 1
            elif (
                letter is not None
                and i + 1 <= len(cont_x)
                and K[i + 1][j] is not None
            ):
                K[i][j] = 1 + K[i + 1][j]
        if j != 0:
            state = transducer_y.states[q_y[j - 1]]
            letter = state.next_letter[0]
            c.add(letter)
    return K


def multiply(transducer_x: Transducer, transducer_y: Transducer) -> Transducer:
    product_transducer = Transducer(None, [], [])
    # Copy each of the existing transducers
    inclusion_x: List[Optional[StateId]] = [
        None for state in transducer_x.states
    ]
    inclusion_y: List[Optional[StateId]] = [
        None for state in transducer_y.states
    ]
    for transducer, inclusion in [
        (transducer_x, inclusion_x),
        (transducer_y, inclusion_y),
    ]:
        for state in transducer.states:
            new_state = product_transducer.add_state(
                [None, None], [None, None], transducer.terminal[state.state_id]
            )
            inclusion[state.state_id] = new_state.state_id

    for transducer, inclusion in [
        (transducer_x, inclusion_x),
        (transducer_y, inclusion_y),
    ]:
        for state in transducer.states:
            inclusion_id = inclusion[state.state_id]
            assert inclusion_id is not None
            product_state = product_transducer.states[inclusion_id]
            for letter in [0, 1]:
                product_state.next_letter[letter] = state.next_letter[letter]
                child = state.next_state[letter]
                if child is not None:
                    inclusion_child_id = inclusion[child.state_id]
                    assert inclusion_child_id is not None
                    product_state.next_state[
                        letter
                    ] = product_transducer.states[inclusion_child_id]

    q_x = transducer_precompute_q(transducer_x, 1)
    q_y = transducer_precompute_q(transducer_y, 0)
    cont_x = transducer_cont(transducer_x)
    cont_y = transducer_cont(transducer_y)
    K0 = compute_k(0, transducer_x, transducer_y)
    K1 = compute_k(1, transducer_x, transducer_y)

    state_lookup: List[List[Optional[StateId]]] = [
        [None for j in range(len(cont_y) + 1)] for i in range(len(cont_x) + 1)
    ]
    reverse_state_lookup: List[Optional[Tuple[int, int]]] = [
        None for state in product_transducer.states
    ]
    for i in range(len(cont_x), -1, -1):
        for j in range(len(cont_y), -1, -1):
            next_state_id: List[Optional[StateId]] = [None, None]
            next_letter: List[Optional[OutputLetter]] = [None, None]
            if K0[i][j] is not None:
                next_state_id[0] = state_lookup[i][j + K0[i][j]]
                next_letter[0] = product_transducer.states[
                    inclusion_y[q_y[j + K0[i][j] - 1]]
                ].next_letter[0]
            else:
                inclusion_state = product_transducer.states[inclusion_x[q_x[i]]]
                if (
                    inclusion_state is not None
                    and inclusion_state.next_state[0] is not None
                ):
                    next_state_id[0] = inclusion_state.next_state[0].state_id
                    next_letter[0] = inclusion_state.next_letter[0]
            if K1[i][j] is not None:
                next_state_id[1] = state_lookup[i + K1[i][j]][j]
                next_letter[1] = product_transducer.states[
                    inclusion_x[q_x[i + K1[i][j] - 1]]
                ].next_letter[1]
            else:
                inclusion_state = product_transducer.states[inclusion_y[q_y[j]]]
                if (
                    inclusion_state is not None
                    and inclusion_state.next_state[1] is not None
                ):
                    next_state_id[1] = inclusion_state.next_state[1].state_id
                    next_letter[1] = inclusion_state.next_letter[1]
            state_lookup[i][j] = product_transducer.add_state(
                next_state_id, next_letter, False
            ).state_id
            reverse_state_lookup.append((i, j))

    product_transducer.initial = state_lookup[0][0]
    for state in product_transducer.states:
        for letter in [0, 1]:
            if (
                state.next_state[letter] is not None
                and reverse_state_lookup[state.next_state[letter].state_id]
                is not None
            ):
                i, j = reverse_state_lookup[state.next_state[letter].state_id]
                if j == len(cont_y):
                    state.next_state[letter] = product_transducer.states[
                        inclusion_x[q_x[i]]
                    ]
                elif i == len(cont_x):
                    state.next_state[letter] = product_transducer.states[
                        inclusion_y[q_y[j]]
                    ]

    return product_transducer
