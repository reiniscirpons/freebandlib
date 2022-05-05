"""Functions for computing the product transducer.

See Section 5 of THEPAPER for more information.
"""

from typing import List, Optional, Tuple

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
        An integer, either 0 or 1.
    transducer_x : Transducer
        A transducer representing :math:`x\in\FB(A)`.
    transducer_y : Transducer
        A transducer representing :math:`y\in\FB(A)`.

    Returns
    -------
    List[List[int]]
        The partial function :math:`\overline{K}_{\alpha}` implemented as a
        two dimensional list.

    Notes
    -----
    Implements the `ComputeK` algorithm of THEPAPER.
    """
    q_x = transducer_precompute_q(transducer_x.initial, 1, transducer_x)
    q_y = transducer_precompute_q(transducer_y.initial, 0, transducer_y)
    cont_x = transducer_cont(transducer_x.initial, transducer_x)
    cont_y = transducer_cont(transducer_y.initial, transducer_y)
    K: List[List[Optional[int]]] = [
        [None for j in range(len(cont_y) + 1)] for i in range(len(cont_x) + 1)
    ]
    c = set()
    if alpha == 0:
        for i in range(len(cont_x), -1, -1):
            for j in range(len(cont_y), -1, -1):
                letter = transducer_y.next_letter[q_y[j]][0]
                if letter is not None and letter not in c:
                    K[i][j] = 1
                elif (
                    letter is not None
                    and j + 1 <= len(cont_y)
                    and K[i][j + 1] is not None
                ):
                    K[i][j] = 1 + K[i][j + 1]
            if i != 0:
                letter = transducer_x.next_letter[q_x[i - 1]][1]
                c.add(letter)
        return K
    # TODO: Remove code duplication
    # alpha == 1
    for j in range(len(cont_y), -1, -1):
        for i in range(len(cont_x), -1, -1):
            letter = transducer_x.next_letter[q_x[i]][1]
            if letter is not None and letter not in c:
                K[i][j] = 1
            elif (
                letter is not None
                and i + 1 <= len(cont_x)
                and K[i + 1][j] is not None
            ):
                K[i][j] = 1 + K[i + 1][j]
        if j != 0:
            letter = transducer_y.next_letter[q_y[j - 1]][0]
            c.add(letter)
    return K


def multiply(transducer_x: Transducer, transducer_y: Transducer) -> Transducer:
    """Compute the product transducer.

    Parameters
    ----------
    transducer_x: Transducer
        A transducer.
    transducer_y: Transducer
        A transducer.

    Returns
    -------
    Transducer
        The product transducer.

    Notes
    -----
    Implements the `Multiply` algorithm of THEPAPER.
    """
    product_transducer = Transducer(None, [], [], [])
    # Copy each of the existing transducers
    inclusion_x: List[Optional[StateId]] = [
        None for state in range(transducer_x.nr_states)
    ]
    inclusion_y: List[Optional[StateId]] = [
        None for state in range(transducer_y.nr_states)
    ]
    for transducer, inclusion in [
        (transducer_x, inclusion_x),
        (transducer_y, inclusion_y),
    ]:
        for state in range(transducer.nr_states):
            inclusion[state] = product_transducer.add_state(
                [None, None], [None, None], transducer.terminal[state]
            )

    for transducer, inclusion in [
        (transducer_x, inclusion_x),
        (transducer_y, inclusion_y),
    ]:
        for state in range(transducer.nr_states):
            product_state = inclusion[state]
            assert product_state is not None
            for letter in [0, 1]:
                product_transducer.next_letter[product_state][
                    letter
                ] = transducer.next_letter[state][letter]
                child = transducer.next_state[state][letter]
                if child is not None:
                    assert inclusion[child] is not None
                    product_transducer.next_state[product_state][
                        letter
                    ] = inclusion[child]

    assert inclusion_x[transducer_x.initial] is not None
    assert inclusion_y[transducer_y.initial] is not None
    q_x = transducer_precompute_q(
        inclusion_x[transducer_x.initial], 1, product_transducer
    )
    q_y = transducer_precompute_q(
        inclusion_y[transducer_y.initial], 0, product_transducer
    )
    cont_x = transducer_cont(transducer_x.initial, transducer_x)
    cont_y = transducer_cont(transducer_y.initial, transducer_y)
    K0 = compute_k(0, transducer_x, transducer_y)
    K1 = compute_k(1, transducer_x, transducer_y)

    state_lookup: List[List[Optional[StateId]]] = [
        [None for j in range(len(cont_y) + 1)] for i in range(len(cont_x) + 1)
    ]
    reverse_state_lookup: List[Optional[Tuple[int, int]]] = [
        None for state in range(product_transducer.nr_states)
    ]
    for i in range(len(cont_x), -1, -1):
        for j in range(len(cont_y), -1, -1):
            next_state: List[Optional[StateId]] = [None, None]
            next_letter: List[Optional[OutputLetter]] = [None, None]
            if K0[i][j] is not None:
                next_state[0] = state_lookup[i][j + K0[i][j]]
                next_letter[0] = product_transducer.next_letter[
                    q_y[j + K0[i][j] - 1]
                ][0]
            else:
                if (
                    q_x[i] is not None
                    and product_transducer.next_state[q_x[i]][0] is not None
                ):
                    next_state[0] = product_transducer.next_state[q_x[i]][0]
                    next_letter[0] = product_transducer.next_letter[q_x[i]][0]
            if K1[i][j] is not None:
                next_state[1] = state_lookup[i + K1[i][j]][j]
                next_letter[1] = product_transducer.next_letter[
                    q_x[i + K1[i][j] - 1]
                ][1]
            else:
                if (
                    q_y[j] is not None
                    and product_transducer.next_state[q_y[j]][1] is not None
                ):
                    next_state[1] = product_transducer.next_state[q_y[j]][1]
                    next_letter[1] = product_transducer.next_letter[q_y[j]][1]
            state_lookup[i][j] = product_transducer.add_state(
                next_state, next_letter, False
            )
            reverse_state_lookup.append((i, j))

    product_transducer.initial = state_lookup[0][0]
    for state in range(product_transducer.nr_states):
        for letter in [0, 1]:
            child = product_transducer.next_state[state][letter]
            if child is not None and reverse_state_lookup[child] is not None:
                i, j = reverse_state_lookup[child]
                if j == len(cont_y):
                    product_transducer.next_state[state][letter] = q_x[i]
                elif i == len(cont_x):
                    product_transducer.next_state[state][letter] = q_y[j]

    return product_transducer
