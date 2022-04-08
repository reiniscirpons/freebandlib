from freebandlib import (
    min_word,
    transducer_minimize,
    treelike_transducer,
    equivalent_words,
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


def test_classify_case():
    w = [0, 1, 0, 2]
    t = transducer_minimize(treelike_transducer(w))
    # assert equivalent_words(min_word(t), w)
    assert min_word(t) == w
