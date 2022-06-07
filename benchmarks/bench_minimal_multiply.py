""" Benchmarks for minimal word """

import os
import sys

sys.path.append(os.path.abspath("../freebandlib"))

import pytest
import pickle
import gzip

import pytest_benchmark

import random

# Fixed seed to ensure determinism when running in paralell
# First 13 digits of the golden ratio.
random.seed(1618033988749)

from pytest_benchmark.utils import safe_dumps


def __save(self, output_json, save):
    output_file = self.get("%s_%s.json" % (self._next_num, save))
    assert not output_file.exists()
    for x in output_json["benchmarks"]:
        del x["params"]
    with output_file.open("wb") as fh:
        fh.write(safe_dumps(output_json, ensure_ascii=True, indent=4).encode())
    self.logger.info("Saved benchmark data in: %s" % output_file)


pytest_benchmark.storage.file.FileStorage.save = __save

from freebandlib import multiply, transducer_cont


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


initial_samples = get_samples("benchmarks/samples/minimal_transducers.gz")
random.shuffle(initial_samples)
samples = []
for transducer_size1, alphabet_size1, transducer1 in initial_samples[:50]:
    for transducer_size2, alphabet_size2, transducer2 in initial_samples[:50]:
        alphabet_size = max(alphabet_size1, alphabet_size2)
        samples.append(
            (
                alphabet_size,
                transducer_size1,
                transducer_size2,
                transducer1,
                transducer2,
            )
        )


@pytest.mark.parametrize(
    "alphabet_size,transducer_size1,transducer_size2,transducer1,transducer2",
    samples,
)
def test_minword(
    benchmark,
    alphabet_size,
    transducer_size1,
    transducer_size2,
    transducer1,
    transducer2,
):
    @benchmark
    def wrapper():
        multiply(transducer1, transducer2)
