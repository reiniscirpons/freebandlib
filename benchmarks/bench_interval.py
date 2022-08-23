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
freebandlib.Transducer.__repr__ = lambda x : ""

samples = []
path = "benchmarks/samples"
for x in sorted(os.listdir(path)):
    if x.startswith("."):
        continue
    sample = pickle.load(open(path + "/" + x, "rb"))
    m = re.search(r"_(\d\d\d\d)_.*_(\d\d\d\d)_", x)
    samples.append((m.group(1), m.group(2), sample))


@pytest.mark.parametrize("alphabet_size,word_length,sample", samples)
def test_interval_transducer_creation(
    benchmark, alphabet_size, word_length, sample
):
    @benchmark
    def wrapper():
        for word in sample:
            interval_transducer(word)
