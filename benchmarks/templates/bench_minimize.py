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

from pytest_benchmark.utils import safe_dumps

from freebandlib import transducer_minimize


def __save(self, output_json, save):
    output_file = self.get("%s_%s.json" % (self._next_num, save))
    assert not output_file.exists()
    for x in output_json["benchmarks"]:
        del x["params"]
    with output_file.open("wb") as fh:
        fh.write(safe_dumps(output_json, ensure_ascii=True, indent=4).encode())
    self.logger.info("Saved benchmark data in: %s" % output_file)


pytest_benchmark.storage.file.FileStorage.save = __save

from freebandlib.transducer import interval_transducer


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
