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

Then inside the `freebandlib` source code directory type:

    pytest

## To run the benchmarks

Download the benchmark data files (i.e. input data for the benchmarks) from:

    TODO(RC)

and put the downloaded archive into the directory `benchmarks/samples`, then
type:

    python3 -m pip install -r benchmarks/requirements.txt
    make benchmark-all

Reference implementations of algorithms for operating with elements in the
free band from the accompanying article **TODO: Article name**.

## TODO:
- [ ] Write article
  - [ ] Preliminaries
  - [x] Synchronous transducer rep
  - [x] Equality checking
  - [x] Multiplication
  - [ ] Minimal word rep
  - [ ] Minimal automaton rep
  - [ ] Pictures
- [ ] Write code
  - [x] Datastructures and types for transducers
  - [ ] Basic operations on transducers
    - [x] Add state
    - [x] Traverse
    - [x] Underlying graph
    - [x] Connected states
    - [x] Topo order
    - [x] Subtransducer
    - [x] Trim
    - [x] Minimize
    - [ ] Disjoint union (for multiplying)
  - [x] Basic operations on words
    - [x] `pref`, `ltof`, `suff`, `ftol`
    - [x] `cont`
    - [x] word function `f_w`
    - [x] rights, lefts
  - [ ] Basic transducer constructions
    - [x] Treelike
    - [x] Interval
    - [x] Minimal
    - [ ] The one you get by right multiplying by a single letter (?)
  - [ ] Multiplication
  - [ ] Minimal word rep
    - [ ] Largest intersection
    - [ ] Iron out details of full algo
  - [ ] Minimal automaton
    - [ ] Figure out theory first
- [ ] Write tests
- [ ] Write docs
