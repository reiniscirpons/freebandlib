"""Transducer multiplication functions.

TODO: Finish
"""

from typing import List

from freebandlib.transducer import (
    Transducer,
    InputLetter,
    transducer_precompute_k,
    transducer_cont,
)


def compute_k(
    alpha: int, transducer_x: Transducer, transducer_y: Transducer
) -> List[List[int]]:
    """Given a transducer return the K function.

    Parameters
    ----------
    alpha: int
        Should be 0 or 1
    transducer_x : Transducer
        A transducer representing :math:`x\\in\\FB(A)`.
    transducer_y : Transducer
        A transducer representing :math:`y\\in\\FB(A)`.

    Returns
    -------
    List[List[int]]
        The partial function :math:`\overline{K}_{\\alpha}` implemented as a
        two dimensional list.
    """
    q_x = transducer_precompute_q(transducer_x, 1)
    q_y = transducer_precompute_q(transducer_y, 0)
    cont_x = transducer_cont(transducer_x)
    cont_y = transducer_cont(transducer_y)
    K = [[None for j in range(len(cont_y) + 1)] for i in range(len(cont_x) + 1)]
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
    inclusion_x = [None for state in transducer_x.states]
    inclusion_y = [None for state in transducer_y.states]
    for transducer in (transducer_x, transducer_y):
        pass
