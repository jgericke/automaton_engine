# Makefile layout borrowed from lumengxi / https://gist.github.com/lumengxi/0ae4645124cd4066f676
.PHONY: clean-pyc clean-build docs clean

help:
	@echo "clean - remove all build, test, coverage artifacts"
	@echo "clean-build - remove build artifacts"
	@echo "clean-pyc - remove python file artifacts"
	@echo "clean-test - remove test and coverage artifacts"
	@echo "clean-docs - remove built docs"
	@echo "lint - check style with flake8"
	@echo "test - run tests quickly with the default Python"
	@echo "coverage - check code coverage quickly with the default Python"
	@echo "docs - generate documentation with mkdocs"
	@echo "release - package and upload a release"
	@echo "dist - package"
	@echo "install - install the package to the active Python's site-packages"

clean: clean-build clean-pyc clean-test clean-docs

clean-build:
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test:
	rm -fr .pytest_cache
	rm -f .coverage
	rm -rf htmlcov

clean-docs:
	rm -fr site

lint:
	flake8 automaton_engine tests

test:
	python setup.py test

coverage:
	coverage run --source automaton_engine setup.py test
	coverage report -m
	coverage html
	$(BROWSER) htmlcov/index.html

docs:
	mkdocs build -c

servedocs:
	mkdocs serve

dist: clean
	python setup.py sdist
	python setup.py bdist_wheel
	ls -l dist	

release: dist
	twine check dist/*
	twine upload dist/*

install: clean
	python setup.py install

build-docker:
	docker build --rm -t automaton-engine:latest -t automaton-engine:1.0.1 .

build-docker-nocache:
	docker build --no-cache -t automaton-engine:latest -t automaton-engine:1.0.1 .