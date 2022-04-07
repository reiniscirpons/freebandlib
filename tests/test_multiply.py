""" Tests for freebandlib.multiply """
import itertools
from random import randint, random, shuffle
from typing import List

import pytest

from freebandlib.multiply import multiply
from freebandlib.transducer import (
    StateId,
    Transducer,
    interval_transducer,
    minimal_transducer,
    transducer_connected_states,
    transducer_induced_subtransducer,
    transducer_isomorphism,
    transducer_minimize,
    transducer_topological_order,
    transducer_trim,
    treelike_transducer,
)
from freebandlib.words import InputLetter, OutputWord, cont, word_function

from .test_transducer import check_transducers_realize_same

_sample_42_words = (
    [4, 1, 4, 2, 1],
    [2, 0, 3, 3, 0],
    [3, 3, 3, 4, 1],
    [1, 1, 4, 4, 0],
    [2, 0, 2, 0, 1],
    [1, 4, 4, 3, 0],
    [4, 1, 3, 2, 0],
    [0, 4, 0, 2, 1],
    [3, 1, 1, 3, 0],
    [2, 0, 0, 2, 1],
    [2, 0, 3, 3, 1],
    [3, 4, 4, 3, 0],
    [4, 1, 2, 3, 0],
    [4, 4, 0, 1, 1],
    [3, 1, 3, 2, 1],
    [3, 4, 4, 1, 0],
    [4, 4, 1, 1, 1],
    [4, 2, 0, 1, 1],
    [3, 3, 1, 3, 0],
    [2, 4, 3, 0, 1],
    [0, 2, 3, 4, 1],
    [3, 2, 1, 2, 0],
    [3, 4, 0, 3, 1],
    [3, 3, 1, 3, 1],
    [0, 2, 4, 2, 1],
    [2, 3, 3, 2, 1],
    [1, 0, 0, 2, 0],
    [1, 1, 1, 2, 0],
    [0, 1, 4, 0, 1],
    [2, 2, 4, 3, 0],
    [2, 0, 4, 2, 0],
    [2, 1, 2, 3, 0],
    [4, 4, 2, 1, 1],
    [3, 4, 3, 2, 0],
    [4, 2, 0, 3, 1],
    [4, 0, 1, 2, 1],
    [4, 1, 3, 1, 1],
    [0, 2, 4, 0, 1],
    [2, 1, 4, 2, 0],
    [1, 3, 1, 4, 1],
    [3, 3, 1, 2, 1],
    [4, 5, 1, 4, 5, 1, 5, 3, 4, 5, 1, 5, 3, 1, 5, 3],
)

_sample_42_more_words = (
    [3, 0, 3, 1, 0, 3, 1, 3],
    [4, 2, 3, 2, 3, 4, 0, 2, 3, 4, 0],
    [3, 2, 0, 3, 2, 0, 2, 1, 3, 2, 0, 2, 1, 0, 2, 1],
    [2, 4, 0, 3, 4, 0, 3, 2],
    [
        0,
        1,
        4,
        3,
        0,
        1,
        4,
        3,
        1,
        4,
        3,
        4,
        2,
        0,
        1,
        4,
        3,
        1,
        4,
        3,
        4,
        2,
        1,
        4,
        3,
        4,
        2,
        3,
        4,
        2,
    ],
    [3, 0, 4, 0, 4, 3, 1, 0, 4, 3, 1],
    [4, 3, 2, 3, 2, 4, 0, 3, 2, 4, 0],
    [3, 4, 1, 0, 3, 4, 1, 0, 4, 1, 0, 1],
    [0, 3, 0, 1, 3, 0, 1, 2, 3, 0, 1, 2, 0, 1, 2, 1],
    [0, 2, 3, 0, 2, 0],
    [4, 1, 2, 0, 1, 2, 0, 4],
    [3, 2, 1, 0, 2, 1, 0, 3],
    [4, 3, 1, 2, 4, 3, 1, 2, 3, 1, 2, 1],
    [0, 2, 4, 0, 2, 4, 2, 3, 0, 2, 4, 2, 3, 4, 2, 3, 2],
    [3, 4, 0, 3, 4, 0, 4, 2, 3, 4, 0, 4, 2, 0, 4, 2],
    [0, 2, 1, 0, 2, 0],
    [
        0,
        1,
        3,
        0,
        1,
        3,
        1,
        2,
        0,
        1,
        3,
        1,
        2,
        3,
        1,
        2,
        4,
        0,
        1,
        3,
        1,
        2,
        3,
        1,
        2,
        4,
        3,
        1,
        2,
        4,
    ],
    [4, 2, 0, 1, 2, 0, 1, 4],
    [0, 3, 0, 1, 3, 0, 1, 2, 3, 0, 1, 2, 0, 1, 2, 1],
    [0, 3, 0, 1, 3, 0, 1, 2, 3, 0, 1, 2, 0, 1, 2, 1],
    [4, 3, 2, 0, 3, 2, 0, 4],
    [4, 0, 1, 2, 4, 0, 1, 2, 0, 1, 2, 1],
    [3, 0, 3, 2, 0, 3, 2, 4, 0, 3, 2, 4],
    [3, 2, 1, 0, 2, 1, 0, 3],
    [0, 1, 3, 2, 3, 2, 0, 1],
    [0, 1, 2, 3, 4, 0, 1, 2, 3, 4, 1, 2, 3, 4, 3, 4, 2],
    [0, 2, 0, 4, 2, 0, 4, 1, 2, 0, 4, 1, 3, 2, 0, 4, 1, 3],
    [4, 0, 2, 0, 4],
    [3, 0, 3, 2, 0, 3, 2, 4, 0, 3, 2, 4],
    [0, 1, 3, 1, 3, 0, 2, 1, 3, 0, 2, 4, 1, 3, 0, 2, 4],
    [0, 1, 4, 1, 4, 0, 3, 1, 4, 0, 3, 4, 0, 3, 0],
    [2, 4, 0, 3, 4, 0, 3, 2],
    [3, 1, 4, 2, 3, 1, 4, 2, 1, 4, 2, 4],
    [2, 4, 1, 0, 3],
    [0, 2, 3, 0, 2, 0],
    [0, 1, 3, 2, 3, 2, 0, 1],
    [4, 3, 1, 2, 4, 3, 1, 2, 3, 1, 2, 1],
    [3, 2, 0, 1, 3, 2, 0, 1, 0, 1, 2],
    [0, 3, 0, 1, 3, 0, 1, 2, 3, 0, 1, 2, 1, 2, 0],
    [2, 4, 1, 0, 3],
    [4, 3, 1, 2, 4, 3, 1, 2, 3, 1, 2, 1],
    [4, 1, 2, 0, 1, 2, 0, 4],
)


def check_multiply(
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
            for constructor3 in transducer_constructors:
                check_transducers_realize_same(
                    w1 + w2, multiply(t1, t2), constructor3(w1 + w2)
                )


def test_transducer_multiply1():
    w = [1, 2, 3, 4, 3, 2, 1]
    check_multiply(w, w)


def test_transducer_multiply2():
    assert len(_sample_42_words) == 42
    transducer_constructors = (interval_transducer,)
    for x in _sample_42_words:
        for y in _sample_42_words:
            check_multiply(x, y, transducer_constructors)


def test_transducer_multiply3():
    assert len(_sample_42_more_words) == 42
    transducer_constructors = (interval_transducer,)
    for x in _sample_42_more_words:
        for y in _sample_42_more_words:
            check_multiply(x, y, transducer_constructors)


def test_transducer_multiply4():
    w1 = [
        8,
        7,
        1,
        3,
        8,
        5,
        11,
        9,
        11,
        2,
        4,
        0,
        4,
        0,
        11,
        4,
        4,
        5,
        6,
        10,
        7,
        2,
        7,
        3,
        5,
        5,
        8,
        9,
        1,
        4,
        9,
        3,
        0,
        7,
        2,
        0,
        1,
        1,
        4,
        7,
        11,
        7,
        9,
        8,
        5,
        7,
        2,
        3,
        11,
        9,
        6,
        11,
        0,
        11,
        10,
        10,
        9,
        10,
        3,
        1,
        5,
        10,
        4,
        6,
        0,
        4,
        11,
        10,
        9,
        4,
        2,
        7,
        3,
        7,
        0,
        10,
        2,
        1,
        8,
        2,
        3,
        5,
        2,
        2,
        6,
        4,
        4,
        7,
        0,
        8,
        11,
        1,
        4,
        4,
        2,
        9,
        9,
        11,
        9,
        4,
    ]
    w2 = [
        1,
        2,
        10,
        0,
        9,
        5,
        10,
        9,
        6,
        5,
        7,
        0,
        0,
        3,
        5,
        0,
        6,
        9,
        8,
        4,
        10,
        2,
        4,
        1,
        10,
        9,
        1,
        1,
        0,
        6,
        8,
        9,
        4,
        6,
        4,
        6,
        5,
        1,
        2,
        7,
        7,
        2,
        2,
        2,
        6,
        0,
        4,
        1,
        2,
        2,
        10,
        8,
        10,
        11,
        11,
        10,
        7,
        7,
        10,
        10,
        11,
        6,
        1,
        11,
        2,
        8,
        6,
        7,
        11,
        9,
        5,
        2,
        10,
        1,
        8,
        1,
        9,
        4,
        0,
        5,
        10,
        4,
        7,
        11,
        9,
        11,
        9,
        4,
        7,
        7,
        3,
        11,
        8,
        2,
        6,
        8,
        2,
        11,
        10,
        0,
    ]
    check_multiply(w1, w2)
