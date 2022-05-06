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
	pytest -n 4 -v benchmarks/bench_interval.py --benchmark-save=interval

benchmark-minimize:
	pytest -n 6 -v benchmarks/bench_minimize_00.py --benchmark-save=minimize
	pytest -n 6 -v benchmarks/bench_minimize_01.py --benchmark-save=minimize
	pytest -n 6 -v benchmarks/bench_minimize_02.py --benchmark-save=minimize
	pytest -n 6 -v benchmarks/bench_minimize_03.py --benchmark-save=minimize
	pytest -n 6 -v benchmarks/bench_minimize_04.py --benchmark-save=minimize
	pytest -n 6 -v benchmarks/bench_minimize_05.py --benchmark-save=minimize
	pytest -n 6 -v benchmarks/bench_minimize_06.py --benchmark-save=minimize
	pytest -n 6 -v benchmarks/bench_minimize_07.py --benchmark-save=minimize
	pytest -n 6 -v benchmarks/bench_minimize_08.py --benchmark-save=minimize
	pytest -n 6 -v benchmarks/bench_minimize_09.py --benchmark-save=minimize
	pytest -n 6 -v benchmarks/bench_minimize_10.py --benchmark-save=minimize
	pytest -n 6 -v benchmarks/bench_minimize_11.py --benchmark-save=minimize
	pytest -n 6 -v benchmarks/bench_minimize_12.py --benchmark-save=minimize
	pytest -n 6 -v benchmarks/bench_minimize_13.py --benchmark-save=minimize
	pytest -n 6 -v benchmarks/bench_minimize_14.py --benchmark-save=minimize
	pytest -n 6 -v benchmarks/bench_minimize_15.py --benchmark-save=minimize
	pytest -n 6 -v benchmarks/bench_minimize_16.py --benchmark-save=minimize
	pytest -n 6 -v benchmarks/bench_minimize_17.py --benchmark-save=minimize
	pytest -n 6 -v benchmarks/bench_minimize_18.py --benchmark-save=minimize
	pytest -n 6 -v benchmarks/bench_minimize_19.py --benchmark-save=minimize

coverage:
	@coverage run --source . --omit="tests/*" -m py.test
	@coverage html
	@echo "See: htmlcov/index.html"
