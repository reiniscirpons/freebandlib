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
