# -*- coding: utf-8 -*-

# Copyright (c) 2022, Reinis Cirpons + J. D. Mitchell
#
# Distributed under the terms of the GPL license version 3.
#
# The full license is in the file LICENSE, distributed with this software.

doc: 
	cd docs && make html

clean-doc:
	rm -rf docs/_build

clean: clean-doc
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

coverage:
	@coverage run --source . --omit="tests/*" -m py.test
	@coverage html
	@echo "See: htmlcov/index.html"
