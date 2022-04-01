""" Tests for freebandlib.words """

from freebandlib.words import pref_ltof, suff_ftol

import pytest


def test_pref_ltof():
    with pytest.raises(TypeError):
        pref_ltof("abac")
    assert pref_ltof([0, 1, 0, 2]) == ([0, 1, 0], 2)
    assert pref_ltof([0, 1, 0]) == ([0], 1)


def test_suff_ltof():
    with pytest.raises(TypeError):
        suff_ftol("abac")

    assert suff_ftol([0, 1, 0, 2]) == ([0, 2], 1)
