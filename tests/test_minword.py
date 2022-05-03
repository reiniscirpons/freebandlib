from freebandlib import (
    min_word,
    transducer_minimize,
    treelike_transducer,
    interval_transducer,
    equal_in_free_band,
)
from freebandlib.minword import Case, classify_case


def test_classify_case():
    w = [0, 1, 0, 2]
    t = transducer_minimize(treelike_transducer(w))
    assert t.nr_states == 6
    assert classify_case(t, 0) == (Case.II, 1)
    assert classify_case(t, 1) == (Case.I, 2)
    assert classify_case(t, 2) == (Case.II, 1)
    assert classify_case(t, 3) == (Case.I, 1)
    assert classify_case(t, 4) == (Case.I, 1)
    assert classify_case(t, 5) == (Case.I, 0)


def test_min_word():
    w = [0, 1, 0, 2]
    t = transducer_minimize(treelike_transducer(w))
    # assert equal_in_free_band(min_word(t), w)
    assert min_word(t) == w

    w = [0, 1, 0, 2]
    t = transducer_minimize(interval_transducer(w))
    # assert equal_in_free_band(min_word(t), w)
    assert min_word(t) == w

    w = [1, 2, 0, 2, 1, 2, 3]
    t = transducer_minimize(interval_transducer(w))
    # assert equal_in_free_band(min_word(t), w)
    assert min_word(t) == w

    w = [4, 0, 4, 2]
    t = transducer_minimize(interval_transducer(w))
    # assert equal_in_free_band(min_word(t), w)
    assert min_word(t) == w

    w = [1, 2, 0, 2, 1, 2, 3, 4, 0, 4, 2]
    t = transducer_minimize(interval_transducer(w))
    # assert equal_in_free_band(min_word(t), w)
    assert min_word(t) == w
