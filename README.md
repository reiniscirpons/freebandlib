![logo](./images/logo.svg)
# Freebandlib

This repository contains reference implementations of the algorithms described
in the paper:

    TODO(RC): authors, title, arxiv url

Algorithm X is called Y in freebandlib TODO(RC) for all algorithms in the
paper.

```python3
something
```

## To run the tests

Type:

    python3 -m pip install -r tests/requirements.txt

Then inside the `freebandlib` top level directory type:

    pytest

## To run the benchmarks

Download the benchmark sample data files (i.e. input data for the benchmarks).
To do so type:

    ./get_benchmark_sample_data.sh

Then type:

    python3 -m pip install -r benchmarks/requirements.txt
    make benchmark-all

It is also possible to generate entirely new benchmark sample data by using the
code in `benchmarks/generate_sample_data.py`. 
TODO(RC): Example of generating benchmarks
