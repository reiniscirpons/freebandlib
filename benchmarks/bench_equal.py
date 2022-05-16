""" Benchmarks for the creation of interval automata """

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

from freebandlib import equal_in_free_band

samples = []
path = "benchmarks/samples"
for x in sorted(os.listdir(path)):
    if x.startswith("."):
        continue
    sample = pickle.load(open(path + "/" + x, "rb"))
    m = re.search(r"_(\d\d\d\d)_.*_(\d\d\d\d)_", x)
    samples.append((m.group(1), m.group(2), sample))

samples_refined = []
for alphabet_size, word_len, sample in samples:
    random.shuffle(sample)
    for word in sample[:10]:
        samples_refined.append((word_len, alphabet_size, word))

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
        equal_in_free_band(word1, word2)
