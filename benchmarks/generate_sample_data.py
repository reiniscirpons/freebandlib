""" Tools for creating the benchmarks for freebandlib """
import itertools
import pickle
import random
import os
import gzip

sys.path.append(os.path.abspath("../freebandlib"))

from freebandlib import interval_transducer, transducer_minimize


def random_word(length_alphabet, length_word):
    return [random.randint(0, length_alphabet) for _ in range(length_word)]


def random_word_sample(length_alphabet, length_word, num_words):
    return [random_word(length_alphabet, length_word) for _ in range(num_words)]


def write_pickle_file(fname, sample, mode="wb"):
    with open(fname, mode) as f:
        pickle.dump(sample, f)


def write_gzip_pickle_file(fname, sample):
    with gzip.open(fname, "ab") as f:
        pickle.dump(sample, f)


def generate_words(alphabet_range, word_range, num_words):
    if not os.path.exists("benchmarks/samples"):
        os.mkdir("benchmarks/samples")
    for length_alphabet in alphabet_range:
        for length_word in word_range:
            fname = f"benchmarks/samples/{num_words:04}_words_{length_alphabet:04}_letters_{length_word:04}_length"
            sample = random_word_sample(length_alphabet, length_word, num_words)
            write_pickle_file(fname, sample)


def generate_interval_transducers():
    path = "benchmarks/samples"
    sample = []
    fname = path + "/interval_transducers.gz"
    if os.path.exists(fname) and os.path.isfile(fname):
        os.remove(fname)
    for i, x in enumerate(sorted(os.listdir(path))):
        if x.startswith(".") or x == "interval_transducers.gz":
            continue
        x = path + "/" + x
        print(f"Processing {x} . . .")
        for sample in pickle.load(open(x, "rb"))[:10]:
            write_gzip_pickle_file(fname, interval_transducer(sample))


def generate_minimal_transducers():
    path = "benchmarks/samples"
    sample = []
    fname = path + "/minimal_transducers.gz"
    if os.path.exists(fname) and os.path.isfile(fname):
        os.remove(fname)
    for i, x in enumerate(sorted(os.listdir(path))):
        if not x.startswith("interval_transducers"):
            continue
        x = path + "/" + x
        print(f"Processing {x} . . .")
        with gzip.open(x, "rb") as f:
            while True:
                try:
                    write_gzip_pickle_file(
                        fname, transducer_minimize(pickle.load(f))
                    )
                except EOFError:
                    break


def split_file(fname, num_parts):
    f = gzip.open(fname, "rb")
    fname = ".".join(fname.split(".")[:-1])
    subfiles = [f"{fname}_{n:02}.gz" for n in range(num_parts)]
    subfiles = [gzip.open(x, "wb") for x in subfiles]
    while True:
        try:
            for n in range(num_parts):
                pickle.dump(pickle.load(f), subfiles[n])
        except EOFError:
            break
