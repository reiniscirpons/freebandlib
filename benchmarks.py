""" Tools for creating the benchmarks for freebandlib """
import itertools
import pickle
import random


def random_word(length_alphabet, length_word):
    return [random.randint(0, length_alphabet) for _ in range(length_word)]


def random_word_sample(length_alphabet, length_word, num_words):
    return [random_word(length_alphabet, length_word) for _ in range(num_words)]


# def random_word(length_alphabet, length_word, length_content):
#    """uniform"""
#    pass


def write_benchmark_sample(fname, sample):
    with open(fname, "wb") as f:
        pickle.dump(sample, f)


# length_alphabet: up to 100 in steps of 5
# length_word: up to 10000 in steps of 500
# num_words: 100


def generate(alphabet_range, word_range, num_words):
    for length_alphabet in alphabet_range:
        for length_word in word_range:
            fname = f"benchmarks/samples/{num_words:04}_words_{length_alphabet:04}_letters_{length_word:04}_length"
            sample = random_word_sample(length_alphabet, length_word, num_words)
            write_benchmark_sample(fname, sample)


# Pre-processing:
#
# 1. Generate a sample of random words (store)
# 2. Generate interval transducers (store)
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
