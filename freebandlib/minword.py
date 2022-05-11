"""Compute the short-lex least word representing a free band element.

See Section 6 of THEPAPER for more information.
"""
# pylint: disable=invalid-name

from enum import Enum
from typing import Tuple, List

from freebandlib.transducer import StateId, Transducer, transducer_cont
from freebandlib.words import OutputWord


class Case(Enum):
    """A simple enum containing the values of the cases from Lemma 5.3."""

    I = 1
    II = 2
    III = 3


def classify_case(t: Transducer, q: StateId) -> Tuple[Case, int]:
    """Given a transducer and a state return the appropriate case of Lemma 5.3.

    Parameters
    ----------
    t: Transducer
        A transducer representing :math:`x\\in\\textrm{FB}(A)`.
    q : StateId
        A value representing a state in t

    Returns
    -------
    Tuple[Case, int]
        The case of Lemma 5.3 that applies, and the relevant value of
        :math:`k`.

    Notes
    -----
    Implements the `ClassifyCase` algorithm of THEPAPER.
    """
    N = len(transducer_cont(q, t))
    if t.next_letter[q][0] == t.next_letter[q][1]:
        return (Case.I, N)
    u, v = t.next_state[q][0], t.next_state[q][1]
    for k in range(N):
        if (
            t.next_letter[u][1] == t.next_letter[q][1]
            and t.next_letter[v][0] == t.next_letter[q][0]
            and t.next_state[u][1] == t.next_state[v][0]
        ):
            return (Case.II, k + 1)
        u, v = t.next_state[u][1], t.next_state[v][0]
        if t.terminal[u] or t.terminal[v]:
            return (Case.III, N)
    assert False


def min_word(t: Transducer) -> OutputWord:
    """Compute the short-lex least word representing the same element as `t`.

    Parameters
    ----------
    t: Transducer
        A transducer representing :math:`x\\in\\textrm{FB}(A)`.

    Returns
    -------
    OutputWord
        The short-lex least word equivalent to :math:`x`.

    Notes
    -----
    Implements a version of the `MinWord` algorithm of THEPAPER.
    """
    # TODO: Move this outside the wrapped function?
    def min_word_recurse(
        t: Transducer,
        q: StateId,
        w: OutputWord,
        l: int,
        B: List[List[Tuple[int, int]]],
    ) -> OutputWord:
        assert q is not None
        s = len(w) - l + 1
        if B[q] is not None:
            i, j = B[q]
            if i == 0 or j == 0:
                return w, B
            return w + w[i + l - 1 : j], B
        w, B = min_word_recurse(t, t.next_state[q][0], w, l, B)
        c, k = classify_case(t, q)
        if c is Case.I:
            w.append(t.next_letter[q][0])
            l = 0
        elif c is Case.II:
            # TODO better way of doing this?
            r: StateId = t.next_state[q][0]
            for _ in range(k):
                r = t.next_state[r][1]
            assert r is not None
            assert B[r] is not None
            i, j = B[r]
            if i == 0 or j == 0 or j < i:
                l = 0
            else:
                l = j - i + 1
        else:
            w.append(t.next_letter[q][0])
            w.append(t.next_letter[q][1])
            l = 0
        w, B = min_word_recurse(t, t.next_state[q][1], w, l, B)
        B[q] = (s, len(w))
        return w, B

    B = [None] * t.nr_states
    for i, sid in enumerate(t.terminal):
        if sid:
            B[i] = (0, 1)
    return min_word_recurse(t, t.initial, [], 0, B)[0]
