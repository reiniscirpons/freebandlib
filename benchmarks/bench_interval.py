""" Benchmarks for the creation of interval automata """

import os
import sys

sys.path.append(os.path.abspath("../freebandlib"))

import pytest
import pickle
import re

import pytest_benchmark

import freebandlib
from freebandlib.transducer import interval_transducer

# Hack to prevent excessive benchmark output
freebandlib.Transducer.__repr__ = lambda x: ""

# An even worse hack to prevent benchmark output
class SilentList:
    def __init__(self, l):
        self.list = l

    def __iter__(self):
        return self.list.__iter__()

    def __repr__(self):
        return ""

    def __str__(self):
        return ""


samples = []
path = "benchmarks/samples"
for x in sorted(os.listdir(path)):
    if x.startswith(".") or x.endswith(".gz"):
        continue
    sample = pickle.load(open(path + "/" + x, "rb"))
    m = re.search(r"_(\d\d\d\d)_.*_(\d\d\d\d)_", x)
    samples.append((m.group(1), m.group(2), SilentList(sample)))


@pytest.mark.parametrize("alphabet_size,word_length,sample", samples)
def test_interval_transducer_creation(
    benchmark, alphabet_size, word_length, sample
):
    @benchmark
    def wrapper():
        for word in sample:
            interval_transducer(word)
