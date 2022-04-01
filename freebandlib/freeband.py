"""Freebandlib: Reference implementations of algorithms for free bands."""

from typing import Callable, Dict, List, Optional, Set, Tuple

from freebandlib.transducer import (
    InputWord,
    OutputLetter,
    OutputWord,
    StateId,
    Transducer,
    TransducerState,
    transducer_isomorphism,
    transducer_minimize,
)

"""
Section 3: Basic operations on words.

TODO: writeup
"""


def cont(word: OutputWord) -> Set[OutputLetter]:
    """Return the content of a word."""
    return set(word)


def pref_ltof(
    word: OutputWord,
) -> Tuple[Optional[OutputWord], Optional[OutputLetter]]:
    """Return the prefix and first to occur last letter of a word."""
    k = len(cont(word))
    j = 0
    seen = set()
    for i, letter in enumerate(word):
        if letter not in seen:
            j += 1
            if j == k:
                return word[:i], letter
            seen.add(letter)
    # Only happens if word is the empty word
    return None, None


def suff_ftol(
    word: OutputWord,
) -> Tuple[Optional[OutputWord], Optional[OutputLetter]]:
    """Return the suffix and last to occur first letter of a word."""
    return pref_ltof(list(reversed(word)))


def word_function(
    word: OutputWord,
) -> Callable[[InputWord], Optional[OutputWord]]:
    """Given a word w return return its associated function f_w."""

    def f_w(input_word: InputWord) -> Optional[OutputWord]:
        result: OutputWord
        current_part: Optional[OutputWord]
        output_letter: Optional[OutputLetter]

        result = []
        current_part = word

        for input_letter in input_word:
            if current_part is None:
                return None
            if input_letter == 0:
                current_part, output_letter = pref_ltof(current_part)
            elif input_letter == 1:
                current_part, output_letter = suff_ftol(current_part)
            assert output_letter is not None
            result.append(output_letter)

        if current_part is None:
            return None
        if len(current_part) == 0:
            return result
        return None

    return f_w


def compute_right(k: int, w: OutputWord) -> List[Optional[int]]:
    """ """
    curr_cont: List[int]
    curr_k: int
    right_k: List[Optional[int]]
    i: int
    j: int

    curr_cont = [0 for _ in range(max(w) + 1)]
    curr_k = 0
    right_k = [None for _ in range(len(w))]
    j = -1
    for i in range(len(w)):
        if i > 0:
            curr_cont[w[i - 1]] -= 1
            if curr_cont[w[i - 1]] == 0:
                curr_k -= 1
        while j < len(w) - 1 and (curr_cont[w[j + 1]] != 0 or curr_k < k):
            j += 1
            if curr_cont[w[j]] == 0:
                curr_k += 1
            curr_cont[w[j]] += 1
        if curr_k == k:
            right_k[i] = j
    return right_k


def compute_left(k: int, w: OutputWord) -> List[Optional[int]]:
    """TODO: description"""
    result = [
        None if x is None else len(w) - 1 - x
        for x in compute_right(k, list(reversed(w)))
    ]
    return list(reversed(result))


"""
Section 4: Examples of transducers realizing f_w.

TODO: writeup
"""


def treelike_transducer(word: OutputWord) -> Transducer:
    """Return the treelike transducer associated with a word."""
    transducer: Transducer
    pref: Optional[OutputWord]
    suff: Optional[OutputWord]
    ltof: Optional[OutputLetter]
    ftol: Optional[OutputLetter]
    transducer_pref: Transducer
    transducer_suff: Transducer
    states: List[TransducerState]
    terminal: List[bool]

    if len(word) == 0:
        transducer = Transducer(
            0, [TransducerState(0, [None, None], [None, None])], [True]
        )
        return transducer

    pref, ltof = pref_ltof(word)
    suff, ftol = suff_ftol(word)
    assert pref is not None
    assert suff is not None
    transducer_pref = treelike_transducer(pref)
    transducer_suff = treelike_transducer(suff)
    assert transducer_pref.initial is not None
    assert transducer_suff.initial is not None

    states = [
        TransducerState(
            0,
            [
                transducer_pref.states[transducer_pref.initial],
                transducer_suff.states[transducer_suff.initial],
            ],
            [ltof, ftol],
        )
    ]
    states.extend(transducer_pref.states)
    states.extend(transducer_suff.states)
    terminal = [False]
    terminal.extend(transducer_pref.terminal)
    terminal.extend(transducer_suff.terminal)
    transducer = Transducer(0, states, terminal)
    return transducer


def interval_transducer(word: OutputWord) -> Transducer:
    """TODO: description"""
    size_cont: int
    right: List[List[Optional[int]]]
    left: List[List[Optional[int]]]
    states: List[TransducerState]
    interval_lookup: Dict[Tuple[int, int], StateId]
    i: Optional[int]
    j: Optional[int]
    rr: Optional[int]
    ll: Optional[int]
    terminal: List[bool]

    size_cont = len(cont(word))
    right = [compute_right(k, word) for k in range(1, size_cont + 1)]
    left = [compute_left(k, word) for k in range(1, size_cont + 1)]

    states = [TransducerState(0, [None, None], [None, None])]
    # We use a hash dictionary to associate to each state representing pair
    # (i, j) the id of the state it corresponds to. This is not strictly
    # speaking linear, however a linear runtime can be achieved for example by
    # using radix sort as in the Radoszewski-Rytter paper.
    interval_lookup = {}
    for k in range(size_cont):
        for i, j in enumerate(right[k]):
            if j is not None and (i, j) not in interval_lookup:
                interval_lookup[(i, j)] = len(states)
                if k == 0:
                    states.append(
                        TransducerState(
                            len(states),
                            [states[0], states[0]],
                            [word[i], word[i]],
                        )
                    )
                else:
                    rr = right[k - 1][i]
                    ll = left[k - 1][j]
                    assert rr is not None
                    assert ll is not None
                    states.append(
                        TransducerState(
                            len(states),
                            [
                                states[interval_lookup[(i, rr)]],
                                states[interval_lookup[(ll, j)]],
                            ],
                            [word[rr + 1], word[ll - 1]],
                        )
                    )
        for j, i in enumerate(left[k]):
            if i is not None and (i, j) not in interval_lookup:
                # TODO: Remove duplicated code
                interval_lookup[(i, j)] = len(states)
                if k == 0:
                    states.append(
                        TransducerState(
                            len(states),
                            [states[0], states[0]],
                            [word[i], word[i]],
                        )
                    )
                else:
                    rr = right[k - 1][i]
                    ll = left[k - 1][j]
                    assert rr is not None
                    assert ll is not None
                    states.append(
                        TransducerState(
                            len(states),
                            [
                                states[interval_lookup[(i, rr)]],
                                states[interval_lookup[(ll, j)]],
                            ],
                            [word[rr + 1], word[ll - 1]],
                        )
                    )

    initial = interval_lookup[(0, len(word) - 1)]
    terminal = [False for _ in range(len(states))]
    terminal[0] = True

    # Store the (i, j) state labels for debugging and visualization purposes
    label: List[str] = [""] * len(states)
    for interval in interval_lookup:
        i, j = interval
        label[interval_lookup[interval]] = str((i + 1, j + 1))
    label[0] = "0"

    return Transducer(initial, states, terminal, label)


def minimal_transducer(word: OutputWord) -> Transducer:
    """ """
    return transducer_minimize(interval_transducer(word))


"""
Section 5: Equality checking

TODO: writeup
"""


def equivalent_words(word1: OutputWord, word2: OutputWord) -> bool:
    """ """
    return transducer_isomorphism(
        minimal_transducer(word1), minimal_transducer(word2)
    )


def equivalent_transducers(
    transducer1: Transducer, transducer2: Transducer
) -> bool:
    """ """
    return transducer_isomorphism(
        transducer_minimize(transducer1), transducer_minimize(transducer2)
    )


"""
Section 6: Multiplication

TODO: writeup
"""

"""
Section 7: Minimal word representative

TODO: writeup
"""
