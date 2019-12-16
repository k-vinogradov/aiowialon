SOURCES=setup.py requirements.txt README.md MANIFEST.in LICENSE aiowialon/

install-dev: requirements-dev.txt
	pip install --requirement requirements-dev.txt

check-code-quality:
	pylint aiowialon
	black --check --diff aiowialon

test: check-code-quality
	python -m pytest -v

build: install-dev $(SOURCES)
	rm dist/*
	python setup.py sdist bdist_wheel

publish: test build
	twine upload dist/*
