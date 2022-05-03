"""Basic operations on words.

See Sections 2, 3 and 4 of THEPAPER for more information.
"""
from __future__ import annotations

from typing import List, Optional, Tuple, Set, Callable

InputLetter = int
OutputLetter = int
OutputWord = List[OutputLetter]
InputWord = List[InputLetter]


def _validate_output_word(word: OutputWord) -> None:
    if not isinstance(word, list):
        raise TypeError("the argument must be a list")
    if not all(lambda x: isinstance(x, int) for x in word):
        raise TypeError("the argument must be a list of integers")


def cont(word: OutputWord) -> Set[OutputLetter]:
    """Return the content of a word.

    Parameters
    ----------
    word: OutputWord
        A word over the output alphabet.

    Returns
    -------
    Set[OutputLetter]
        The set of letters occuring in `word`.
    """
    return set(word)


def pref_ltof(
    word: OutputWord,
) -> Tuple[Optional[OutputWord], Optional[OutputLetter]]:
    """Return the prefix and first to occur last letter of a word.

    Either both returned values are `None` or neither is `None`.

    Parameters
    ----------
    word: OutputWord
        A word over the output alphabet.

    Returns
    -------
    Optional[OutputWord]
        The largest prefix of `word` containing one less letter in its content
        than `word`, or `None` if no such prefix exists.
    Optional[OutputLetter]
        The letter after the prefix defined above, or `None` if no such prefix
        exists.
    """
    _validate_output_word(word)

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
    """Return the suffix and last to occur first letter of a word.

    Either both returned values are `None` or neither is `None`.

    Parameters
    ----------
    word: OutputWord
        A word over the output alphabet.

    Returns
    -------
    Optional[OutputWord]
        The largest suffix of `word` containing one less letter in its content
        than `word`, or `None` if no such prefix exists.
    Optional[OutputLetter]
        The letter before the suffix defined above, or `None` if no such suffix
        exists.

    See Also
    --------
    pref_ltof: The dual of this function.
    """
    _validate_output_word(word)
    suff, ftol = pref_ltof(list(reversed(word)))
    return (list(reversed(suff)), ftol) if suff is not None else (None, None)


def word_function(
    word: OutputWord,
) -> Callable[[InputWord], Optional[OutputWord]]:
    """Given a word :math:`w` return its associated word function :math:`f_w`.

    Parameters
    ----------
    word: OutputWord
        A word over the output alphabet.

    Returns
    -------
    Callable[[InputWord], Optional[OutputWord]]
        A partial function that takes an input word and returns an output word
        where defined.

    Notes
    -----
    The word function :math:`f_w` is defined in Definition 3.1 of THEPAPER. Any
    transducer representing `word` in a free band realizes
    `word_function(word)`.
    """

    def f_w(input_word: InputWord) -> Optional[OutputWord]:

        result: OutputWord = []
        current_part: Optional[OutputWord] = word
        for input_letter in input_word:
            output_letter: Optional[OutputLetter] = None
            if current_part is None or len(current_part) == 0:
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


def compute_right(k: int, word: OutputWord) -> List[Optional[int]]:
    """Precompute the prefix maximal content-`k` subwords of `word`.

    Parameters
    ----------
    k: int
        Size of the content of the subwords.
    word: OutputWord
        A word over the output alphabet.

    Returns
    -------
    right_k: List[Optional[int]]
        A list of indices such that `word[i:right_k[i]+1]` is the unique prefix
        maximal content-`k` subword of `word` starting at index `i`, if such a
        subword exists, and `right_k[i] = None` otherwise.

    Notes
    -----
    Implements the `Compute_RIGHT2` method of RR2010aa.
    """
    w = word
    curr_cont: List[int] = [0 for _ in range(max(w) + 1)]
    curr_k: int = 0
    right_k: List[Optional[int]] = [None for _ in range(len(w))]
    j: int = -1
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


def compute_left(k: int, word: OutputWord) -> List[Optional[int]]:
    """Precompute the suffix maximal content-`k` subwords of `word`.

    Parameters
    ----------
    k: int
        Size of the content of the subwords.
    word: OutputWord
        A word over the output alphabet.

    Returns
    -------
    left_k: List[Optional[int]]
        A list of indices such that `word[left_k[j]:j+1]` is the unique prefix
        maximal content-`k` subword of `word` ending at index `j`, if such a
        subword exists, and `left_k[j] = None` otherwise.

    See Also
    --------
    compute_right: For precomputing the prefix maximal content-`k` subwords.
    """
    result = [
        None if x is None else len(word) - 1 - x
        for x in compute_right(k, list(reversed(word)))
    ]
    return list(reversed(result))
