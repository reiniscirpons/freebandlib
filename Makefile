clean: 
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
