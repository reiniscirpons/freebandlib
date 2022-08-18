# -*- coding: utf-8 -*-

# Copyright (c) 2022, Reinis Cirpons + J. D. Mitchell
#
# Distributed under the terms of the GPL license version 3.
#
# The full license is in the file LICENSE, distributed with this software.

doc:
	cd docs && make html

clean-benchmarks:
	rm -rf .benchmarks
	rm -f benchmarks/bench_minimize_*.py
	rm -f benchmarks/bench_interval_multiply_*.py

clean-prof:
	rm -rf prof

clean-doc:
	rm -rf docs/_build

clean: clean-doc clean-prof clean-benchmarks
	rm -rf *.egg-info
	rm -rf docs/build
	rm -rf build/
	rm -rf __pycache__/
	rm -rf dist/
	rm -rf htmlcov/
	rm -rf *.egg-info
	rm -rf .tox
	rm -rf tests/__pycache__
	rm -rf freebandlib/__pycache__

superclean: clean
	git clean -xdf --exclude *.swp --exclude *.swo

.PHONY: superclean

benchmark-interval:
	pytest -n auto -v benchmarks/bench_interval.py --benchmark-save=interval

benchmark-equal:
	pytest -n auto -v benchmarks/bench_equal.py --benchmark-save=equal

INTERVAL_TEST_CASES = 00 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19

benchmark-minimize-generate-benchmarks:
	$(foreach var,$(INTERVAL_TEST_CASES),sed 's/{{NUM}}/$(var)/g' ./benchmarks/templates/bench_minimize.py > ./benchmarks/bench_minimize_$(var).py;)

benchmark-interval-multiply-generate-benchmarks:
	$(foreach var,$(INTERVAL_TEST_CASES),sed 's/{{NUM}}/$(var)/g' ./benchmarks/templates/bench_interval_multiply.py > ./benchmarks/bench_interval_multiply_$(var).py;)

benchmark-minimize: benchmark-minimize-generate-benchmarks
	$(foreach var,$(INTERVAL_TEST_CASES),pytest -n 6 -v benchmarks/bench_minimize_$(var).py --benchmark-save=minimize;)

benchmark-interval-multiply: benchmark-interval-multiply-generate-benchmarks
	$(foreach var,$(INTERVAL_TEST_CASES),pytest -n 6 -v benchmarks/bench_interval_multiply_$(var).py --benchmark-save=interval_multiply;)

benchmark-minimal-multiply:
	pytest -n auto -v benchmarks/bench_minimal_multiply.py --benchmark-save=minimal_multiply

benchmark-isomorphism:
	pytest -n auto -v benchmarks/bench_isomorphism.py --benchmark-save=isomorphism

benchmark-minword:
	pytest -n auto -v benchmarks/bench_minword.py --benchmark-save=minword

benchmark-all: benchmark-interval benchmark-equal  benchmark-minimize benchmark-interval-multiply benchmark-minimal-multiply benchmark-isomorphism benchmark-minword

coverage:
	@coverage run --source . --omit="tests/*" -m py.test
	@coverage html
	@echo "See: htmlcov/index.html"
