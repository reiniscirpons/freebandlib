""" Benchmarks for minimal word """

import os
import sys

sys.path.append(os.path.abspath("../freebandlib"))

import pytest
import pickle
import gzip

import pytest_benchmark

import freebandlib
from freebandlib import min_word, transducer_cont

# Hack to prevent excessive benchmark output
freebandlib.Transducer.__repr__ = lambda x : ""

def get_samples(fnam):
    f = gzip.open(fnam, "rb")
    samples = []
    while True:
        try:
            samples.append(pickle.load(f))
        except EOFError:
            break
    samples = [
        (x.nr_states, max(transducer_cont(x.initial, x)), x) for x in samples
    ]
    return samples


samples = get_samples("benchmarks/samples/minimal_transducers.gz")


@pytest.mark.parametrize("transducer_size,alphabet_size,transducer", samples)
def test_minword(benchmark, transducer_size, alphabet_size, transducer):
    @benchmark
    def wrapper():
        min_word(transducer)
