""" Benchmarks for the minimization of the interval automata

This file is auto-generated from templates/bench_minimize!!!
DO NOT EDIT
"""

import os
import sys

sys.path.append(os.path.abspath("../freebandlib"))

import pytest
import gzip
import pickle

import pytest_benchmark

import freebandlib
from freebandlib import transducer_minimize

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
    samples = [(x.nr_states, x) for x in samples]
    return samples


samples = get_samples("benchmarks/samples/interval_transducers_{{NUM}}.gz")


@pytest.mark.parametrize("nr_states,transducer", samples)
def test_transducer_minimize(benchmark, nr_states, transducer):
    @benchmark
    def wrapper():
        transducer_minimize(transducer)
