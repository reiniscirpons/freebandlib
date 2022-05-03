"""Functions for testing equality of words in the free band.

See Section 4 of THEPAPER for more information.
"""

from freebandlib.transducer import (
    OutputWord,
    Transducer,
    transducer_isomorphism,
    transducer_minimize,
    minimal_transducer,
)


def equal_in_free_band(word1: OutputWord, word2: OutputWord) -> bool:
    """Check if two words are equal in a free band.

    Parameters
    ----------
    word1: OutputWord
        A word over the output alphabet.
    word2: OutputWord
        A word over the output alphabet.

    Returns
    -------
    bool
        `True` if `word1` and `word2` are equal in a free band
        and `False` otherwise.

    Notes
    -----
    The alphabet of the underlying free band is implicitly assumed to be the
    the union of the content of `word1` and `word2`. Implements the
    `EqualInFreeBand` algorithm of THEPAPER.
    """
    return transducer_isomorphism(
        minimal_transducer(word1), minimal_transducer(word2)
    )


def equivalent_transducers(
    transducer1: Transducer, transducer2: Transducer
) -> bool:
    """Check if two transducers represent the same element in the free band.

    Parameters
    ----------
    transducer1: Transducer
        A transducer.
    transducer2: Transducer
        A transducer.

    Returns
    -------
    bool
        `True` if `transducer1` and `transducer2` represent the same element in
        the free band and `False` otherwise.

    Notes
    -----
    The alphabet of the underlying free band is implicitly assumed to be the
    the union of the content of the elements represented by `transducer1` and
    `transducer2`.
    """
    return transducer_isomorphism(
        transducer_minimize(transducer1), transducer_minimize(transducer2)
    )
