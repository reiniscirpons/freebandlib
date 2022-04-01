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
