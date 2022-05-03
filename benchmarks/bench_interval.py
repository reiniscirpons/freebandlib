""" Benchmarks for the creation of interval automata """

import os
import sys

sys.path.append(os.path.abspath("../freebandlib"))

import pytest
import pickle
import re

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

from freebandlib.transducer import interval_transducer

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
