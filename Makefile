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
define benchmark_function
	pytest -n auto -v benchmarks/bench_$(1).py --benchmark-storage=file://./benchmarks/raw_benchmark_data/ --benchmark-save=$(2)
endef

benchmark-minimize-generate-benchmarks:
	$(foreach var,$(INTERVAL_TEST_CASES),sed 's/{{NUM}}/$(var)/g' ./benchmarks/templates/bench_minimize.py > ./benchmarks/bench_minimize_$(var).py;)

benchmark-interval-multiply-generate-benchmarks:
	$(foreach var,$(INTERVAL_TEST_CASES),sed 's/{{NUM}}/$(var)/g' ./benchmarks/templates/bench_interval_multiply.py > ./benchmarks/bench_interval_multiply_$(var).py;)

benchmark-minimize: benchmark-minimize-generate-benchmarks
	mkdir -p ./benchmarks/raw_benchmark_data/
	rm -f ./benchmarks/raw_benchmark_data/*/*_minimize.json
	$(foreach var,$(INTERVAL_TEST_CASES),$(call benchmark_function,minimize_$(var),minimize);)

benchmark-interval-multiply: benchmark-interval-multiply-generate-benchmarks
	mkdir -p ./benchmarks/raw_benchmark_data/
	rm -f ./benchmarks/raw_benchmark_data/*/*_interval_multiply.json
	$(foreach var,$(INTERVAL_TEST_CASES),$(call benchmark_function,interval_multiply_$(var),interval_multiply);)

benchmark-minimal-multiply:
	mkdir -p ./benchmarks/raw_benchmark_data/
	rm -f ./benchmarks/raw_benchmark_data/*/*_minimal_multiply.json
	$(call benchmark_function,minimal_multiply,minimal_multiply)

benchmark-isomorphism:
	mkdir -p ./benchmarks/raw_benchmark_data/
	rm -f ./benchmarks/raw_benchmark_data/*/*_isomorphism.json
	$(call benchmark_function,isomorphism,isomorphism)

benchmark-minword:
	mkdir -p ./benchmarks/raw_benchmark_data/
	rm -f ./benchmarks/raw_benchmark_data/*/*_minword.json
	$(call benchmark_function,minword,minword)

benchmark-all: benchmark-interval benchmark-equal  benchmark-minimize benchmark-interval-multiply benchmark-minimal-multiply benchmark-isomorphism benchmark-minword

coverage:
	@coverage run --source . --omit="tests/*" -m py.test
	@coverage html
	@echo "See: htmlcov/index.html"
