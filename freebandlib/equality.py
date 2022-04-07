"""
Section 5: Equality checking

TODO: writeup
"""

from freebandlib.transducer import (
    OutputWord,
    Transducer,
    transducer_isomorphism,
    transducer_minimize,
    minimal_transducer,
)

from freebandlib.transducer import (
    interval_transducer,
    treelike_transducer,
)


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
