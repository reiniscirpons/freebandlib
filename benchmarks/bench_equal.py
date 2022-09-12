""" Benchmarks for equality of words in the free band """

import os
import sys

sys.path.append(os.path.abspath("../freebandlib"))

import pytest
import pickle
import re

import random

# Fixed seed to ensure determinism when running in paralell
# First 13 digits of the golden ratio.
random.seed(1618033988749)

import pytest_benchmark

import freebandlib
from freebandlib import equal_in_free_band

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
    samples.append((m.group(1), m.group(2), sample))

samples_refined = []
for alphabet_size, word_len, sample in samples:
    random.shuffle(sample)
    for word in sample[:10]:
        samples_refined.append((word_len, alphabet_size, SilentList(word)))

samples = []
for word_len1, alphabet_size1, sample1 in samples_refined:
    for word_len2, alphabet_size2, sample2 in samples_refined:
        samples.append(
            (
                word_len1,
                alphabet_size1,
                word_len2,
                alphabet_size2,
                sample1,
                sample2,
            )
        )

random.shuffle(samples)
samples = samples[:10000]


@pytest.mark.parametrize(
    "word_len1, alphabet_size1, word_len2, alphabet_size2, word1, word2",
    samples,
)
def test_equal_in_free_band(
    benchmark,
    word_len1,
    alphabet_size1,
    word_len2,
    alphabet_size2,
    word1,
    word2,
):
    @benchmark
    def wrapper():
        equal_in_free_band(word1.list, word2.list)
