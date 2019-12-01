install-dev:
	pip install --requirement requirements-dev.txt

check-code-quality:
	pylint aiowialon
	black --check --diff aiowialon

test: check-code-quality
	python -m pytest -v