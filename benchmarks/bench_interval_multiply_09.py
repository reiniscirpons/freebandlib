""" Benchmarks for the multiplication of the interval automata

This file is auto-generated from templates/bench_interval_multiply!!!
DO NOT EDIT
"""

import os
import sys

sys.path.append(os.path.abspath("../freebandlib"))

import pytest
import gzip
import pickle

import random

# Fixed seed to ensure determinism when running in paralell
# First 13 digits of the golden ratio.
random.seed(1618033988749)

import pytest_benchmark

from pytest_benchmark.utils import safe_dumps

from freebandlib import multiply, transducer_cont


def __save(self, output_json, save):
    output_file = self.get("%s_%s.json" % (self._next_num, save))
    assert not output_file.exists()
    for x in output_json["benchmarks"]:
        del x["params"]
    with output_file.open("wb") as fh:
        fh.write(safe_dumps(output_json, ensure_ascii=True, indent=4).encode())
    self.logger.info("Saved benchmark data in: %s" % output_file)


pytest_benchmark.storage.file.FileStorage.save = __save


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


initial_samples = get_samples(
    "benchmarks/samples/interval_transducers_09.gz"
)
random.shuffle(initial_samples)
samples = []
for nr_states1, transducer1 in initial_samples[:5]:
    for nr_states2, transducer2 in initial_samples[:5]:
        alph_size = max(
            max(transducer_cont(transducer1.initial, transducer1)),
            max(transducer_cont(transducer2.initial, transducer2)),
        )
        samples.append(
            (alph_size, nr_states1, nr_states2, transducer1, transducer2)
        )


@pytest.mark.parametrize(
    "alph_size,nr_states1,nr_states2,transducer1,transducer2", samples
)
def test_multiply(
    benchmark, alph_size, nr_states1, nr_states2, transducer1, transducer2
):
    @benchmark
    def wrapper():
        multiply(transducer1, transducer2)
