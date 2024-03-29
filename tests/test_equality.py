""" Tests for freebandlib.multiply """

import itertools
from random import randint, random, shuffle
from typing import List

import pytest
from freebandlib.equality import equal_in_free_band, equivalent_transducers
from freebandlib.transducer import interval_transducer, treelike_transducer
from freebandlib.words import InputLetter, OutputWord, cont, word_function

_sample_free_band_3 = [
    [1],
    [2],
    [3],
    [1, 2],
    [1, 3],
    [2, 1],
    [2, 3],
    [3, 1],
    [3, 2],
    [1, 2, 1],
    [1, 2, 3],
    [1, 3, 1],
    [1, 3, 2],
    [2, 1, 2],
    [2, 1, 3],
    [2, 3, 1],
    [2, 3, 2],
    [3, 1, 2],
    [3, 1, 3],
    [3, 2, 1],
    [3, 2, 3],
    [1, 2, 1, 3, 2, 1, 3],
    [1, 2, 3, 2, 3, 1],
    [1, 2, 3, 1, 2, 3, 2],
    [1, 3, 1, 2, 3, 1, 2],
    [1, 3, 2, 3, 2, 1],
    [1, 3, 2, 1, 3, 2, 3],
    [2, 1, 2, 3, 1, 2, 3],
    [2, 1, 3, 2, 1, 3, 1],
    [2, 1, 3, 1, 3, 2],
    [2, 3, 1, 3, 1, 2],
    [2, 3, 1, 2, 3, 1, 3],
    [2, 3, 2, 1, 3, 2, 1],
    [3, 1, 2, 3, 1, 2, 1],
    [3, 1, 2, 1, 2, 3],
    [3, 1, 3, 2, 1, 3, 2],
    [3, 2, 1, 3, 2, 1, 2],
    [3, 2, 1, 2, 1, 3],
    [3, 2, 3, 1, 2, 3, 1],
    [1, 2, 1, 3, 2, 1, 3, 1],
    [1, 2, 1, 3, 1, 3, 2],
    [1, 2, 3, 1, 2],
    [1, 2, 3, 2, 3, 1, 3],
    [1, 2, 3, 2, 1],
    [1, 3, 1, 2, 3, 1, 2, 1],
    [1, 3, 1, 2, 1, 2, 3],
    [1, 3, 2, 3, 2, 1, 2],
    [1, 3, 2, 1, 3],
    [1, 3, 2, 3, 1],
    [2, 1, 2, 3, 2, 3, 1],
    [2, 1, 2, 3, 1, 2, 3, 2],
    [2, 1, 3, 1, 2],
    [2, 1, 3, 2, 1],
    [2, 1, 3, 1, 3, 2, 3],
    [2, 3, 1, 3, 1, 2, 1],
    [2, 3, 1, 2, 3],
    [2, 3, 1, 3, 2],
    [2, 3, 2, 1, 3, 2, 1, 2],
    [2, 3, 2, 1, 2, 1, 3],
    [3, 1, 2, 1, 3],
    [3, 1, 2, 3, 1],
    [3, 1, 2, 1, 2, 3, 2],
    [3, 1, 3, 2, 3, 2, 1],
    [3, 1, 3, 2, 1, 3, 2, 3],
    [3, 2, 1, 2, 3],
    [3, 2, 1, 2, 1, 3, 1],
    [3, 2, 1, 3, 2],
    [3, 2, 3, 1, 3, 1, 2],
    [3, 2, 3, 1, 2, 3, 1, 3],
    [1, 2, 1, 3, 1, 2],
    [1, 2, 1, 3, 2, 1],
    [1, 2, 1, 3, 1, 3, 2, 3],
    [1, 2, 3, 1, 2, 1],
    [1, 2, 3, 1, 3, 2],
    [1, 2, 3, 2, 1, 2],
    [1, 2, 3, 2, 1, 3],
    [1, 3, 1, 2, 1, 3],
    [1, 3, 1, 2, 3, 1],
    [1, 3, 1, 2, 1, 2, 3, 2],
    [1, 3, 2, 1, 2, 3],
    [1, 3, 2, 1, 3, 1],
    [1, 3, 2, 3, 1, 2],
    [1, 3, 2, 3, 1, 3],
    [2, 1, 2, 3, 1, 2],
    [2, 1, 2, 3, 2, 3, 1, 3],
    [2, 1, 2, 3, 2, 1],
    [2, 1, 3, 1, 2, 1],
    [2, 1, 3, 1, 2, 3],
    [2, 1, 3, 2, 1, 2],
    [2, 1, 3, 2, 3, 1],
    [2, 3, 1, 2, 1, 3],
    [2, 3, 1, 2, 3, 2],
    [2, 3, 1, 3, 2, 1],
    [2, 3, 1, 3, 2, 3],
    [2, 3, 2, 1, 2, 3],
    [2, 3, 2, 1, 2, 1, 3, 1],
    [2, 3, 2, 1, 3, 2],
    [3, 1, 2, 1, 3, 1],
    [3, 1, 2, 1, 3, 2],
    [3, 1, 2, 3, 1, 3],
    [3, 1, 2, 3, 2, 1],
    [3, 1, 3, 2, 3, 2, 1, 2],
    [3, 1, 3, 2, 1, 3],
    [3, 1, 3, 2, 3, 1],
    [3, 2, 1, 2, 3, 1],
    [3, 2, 1, 2, 3, 2],
    [3, 2, 1, 3, 1, 2],
    [3, 2, 1, 3, 2, 3],
    [3, 2, 3, 1, 3, 1, 2, 1],
    [3, 2, 3, 1, 2, 3],
    [3, 2, 3, 1, 3, 2],
    [1, 2, 1, 3, 1, 2, 1],
    [1, 2, 1, 3, 1, 2, 3],
    [1, 2, 1, 3, 2, 1, 2],
    [1, 2, 1, 3, 2, 3, 1],
    [1, 2, 3, 1, 3, 2, 3],
    [1, 2, 3, 2, 1, 3, 1],
    [1, 3, 1, 2, 1, 3, 1],
    [1, 3, 1, 2, 1, 3, 2],
    [1, 3, 1, 2, 3, 1, 3],
    [1, 3, 1, 2, 3, 2, 1],
    [1, 3, 2, 1, 2, 3, 2],
    [1, 3, 2, 3, 1, 2, 1],
    [2, 1, 2, 3, 1, 2, 1],
    [2, 1, 2, 3, 1, 3, 2],
    [2, 1, 2, 3, 2, 1, 2],
    [2, 1, 2, 3, 2, 1, 3],
    [2, 1, 3, 1, 2, 3, 2],
    [2, 1, 3, 2, 3, 1, 3],
    [2, 3, 1, 2, 1, 3, 1],
    [2, 3, 1, 3, 2, 1, 2],
    [2, 3, 2, 1, 2, 3, 1],
    [2, 3, 2, 1, 2, 3, 2],
    [2, 3, 2, 1, 3, 1, 2],
    [2, 3, 2, 1, 3, 2, 3],
    [3, 1, 2, 1, 3, 2, 3],
    [3, 1, 2, 3, 2, 1, 2],
    [3, 1, 3, 2, 1, 2, 3],
    [3, 1, 3, 2, 1, 3, 1],
    [3, 1, 3, 2, 3, 1, 2],
    [3, 1, 3, 2, 3, 1, 3],
    [3, 2, 1, 2, 3, 1, 3],
    [3, 2, 1, 3, 1, 2, 1],
    [3, 2, 3, 1, 2, 1, 3],
    [3, 2, 3, 1, 2, 3, 2],
    [3, 2, 3, 1, 3, 2, 1],
    [3, 2, 3, 1, 3, 2, 3],
    [1, 2, 1, 3, 1, 2, 3, 2],
    [1, 2, 1, 3, 2, 3, 1, 3],
    [1, 3, 1, 2, 1, 3, 2, 3],
    [1, 3, 1, 2, 3, 2, 1, 2],
    [2, 1, 2, 3, 1, 3, 2, 3],
    [2, 1, 2, 3, 2, 1, 3, 1],
    [2, 3, 2, 1, 2, 3, 1, 3],
    [2, 3, 2, 1, 3, 1, 2, 1],
    [3, 1, 3, 2, 1, 2, 3, 2],
    [3, 1, 3, 2, 3, 1, 2, 1],
    [3, 2, 3, 1, 2, 1, 3, 1],
    [3, 2, 3, 1, 3, 2, 1, 2],
]


def check_equivalent_transducers(
    w1: OutputWord,
    w2: OutputWord,
    transducer_constructors=(
        treelike_transducer,
        interval_transducer,
    ),
) -> None:
    for constructor1 in transducer_constructors:
        t1 = constructor1(w1)
        for constructor2 in transducer_constructors:
            t2 = constructor2(w2)
            assert equivalent_transducers(t1, t2)


def test_equal_in_free_band():
    w1 = [1, 4, 2, 3, 10]
    w2 = [1, 4, 1, 4, 2, 3, 10]
    assert equal_in_free_band(w1, w2)
    assert equal_in_free_band(w2, w1)
    assert not equal_in_free_band([1, 4, 1, 4, 2, 10], w1)
    assert not equal_in_free_band(w1, [1, 4, 1, 4, 2, 10])
    assert not equal_in_free_band(w2, [1, 4, 1, 4, 2, 10])
    assert not equal_in_free_band([1, 4, 1, 4, 2, 10], w2)

    w1 = [
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        1,
        0,
        1,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        1,
        1,
        1,
        1,
        1,
    ]
    w2 = [0, 1]
    assert equal_in_free_band(w1, w2)
    assert equal_in_free_band(w2, w1)

    assert not equal_in_free_band([0], [1])
    # assert equal_in_free_band([], [])
    # assert not equal_in_free_band([], [0])

    w1 = [0, 1, 2, 1, 2, 2, 2, 1, 0, 1, 0, 2, 0, 1]
    w2 = [0, 1, 2, 0, 1]
    assert equal_in_free_band(w1, w2)
    assert equal_in_free_band(w2, w1)

    w1, w2 = [0, 1, 0, 2], [0, 1, 0, 3]
    assert not equal_in_free_band(w1, w2)
    assert not equal_in_free_band(w2, w1)

    w1, w2 = [1], [2, 2, 2]
    assert not equal_in_free_band(w1, w2)
    assert not equal_in_free_band(w2, w1)


def test_equivalent_transducers():
    w1 = [1, 4, 2, 3, 10]
    w2 = [1, 4, 1, 4, 2, 3, 10]
    check_equivalent_transducers(w1, w2)
    check_equivalent_transducers(w2, w1)
    w1 = [
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        1,
        0,
        1,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        1,
        1,
        1,
        1,
        1,
    ]
    w2 = [0, 1]
    check_equivalent_transducers(w1, w2)
    check_equivalent_transducers(w2, w1)


def test_inequal_in_free_band():
    for i, x in enumerate(_sample_free_band_3):
        for y in _sample_free_band_3[i + 1 :]:
            assert not equal_in_free_band(x, y)


# Take 120s
# def test_size_free_band():
#     n = 3
#     words = []
#     for i in range(1, 2 ** n + 1):
#         for x in itertools.product(*[list(range(n))] * i):
#             for w in words:
#                 if equal_in_free_band(x, w):
#                     break
#             else:
#                 words.append(x)
#     # assert words == []
#     assert len(words) == 159
