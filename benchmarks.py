""" Tools for creating the benchmarks for freebandlib """
import itertools
import pickle
import random
import os
import gzip

from freebandlib import interval_transducer


def random_word(length_alphabet, length_word):
    return [random.randint(0, length_alphabet) for _ in range(length_word)]


def random_word_sample(length_alphabet, length_word, num_words):
    return [random_word(length_alphabet, length_word) for _ in range(num_words)]


# def random_word(length_alphabet, length_word, length_content):
#    """uniform"""
#    pass


def write_pickle_file(fname, sample, mode="wb"):
    with open(fname, mode) as f:
        pickle.dump(sample, f)


def write_gzip_pickle_file(fname, sample):
    with gzip.open(fname, "ab") as f:
        pickle.dump(sample, f)


# length_alphabet: up to 100 in steps of 5
# length_word: up to 10000 in steps of 500
# num_words: 100


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


# Pre-processing:
#
# 1. Generate a sample of random words (store) X
# 2. Generate interval transducers (store) X
# 3. Minimize the transducers from 2. (store)
# 4. Random words over a given alphabet + content and generate pairs of them

# Benchmarks
# 1. Benchmark creation of interval transducers from words
# 2. Benchmark minimization
# 3. Benchmark isomorphism checking of minimized transducers
# 4. Benchmark equality checking of pairs of words (1 + 2 + 3)
# 5. Benchmark multiplication on interval transducers
# 6. Benchmark multiplication on minimal transducers
# 7. Min. word of minimal transducers
